-- Distinctive Mark: ruling fact check stage bot.
--
-- Runs when a ruling story enters the reporting stage. Follows the ruling-fact-check skill
-- (.claude/skills/ruling-fact-check/SKILL.md) and fetches the editorial rules from the newsroom at run time.
-- It never changes the stage and never publishes: the engine moves the story on after a successful run
-- that returns a version and does not hold. Run from the repository root so the skill path resolves.

local done = require("tactus.tools.done")

Toolset "papyrus" {
    type = "plugin",
    modules = {"papyrus_newsroom.tactus_tools"}
}

ruling_fact_checker = Agent {
    provider = "openai",
    model = "gpt-6-luna",
    system_prompt = [[
You are Distinctive Mark's fact checker for TTAB ruling pages. You did not write the draft.
Follow the ruling-fact-check skill step by step. Use the papyrus tools for everything:
papyrus_editorial_context for the rules, papyrus_story_versions and papyrus_story_version to read the
draft, papyrus_fetch_pdf_text to read every page of the opinion, and papyrus_save_story_version to
record one corrected version only if something changed. Never change the stage. Never publish.
When finished, call done.
]],
    skills = {".claude/skills/ruling-fact-check"},
    skills_mode = "full",
    tools = {"papyrus", done},
    output = {
        version = field.string{required = true, description = "New version id if a correction was saved, else an empty string"},
        corrections = field.array{required = true},
        unverifiable = field.array{required = true},
        opinion_read = field.boolean{required = true}
    }
}

local MAXIMUM_WORK_TURNS = 12
local MAXIMUM_REPORT_ATTEMPTS = 3

local function work_until_done_then_report(agent, first_message)
    done.reset()
    agent{message = first_message}
    local turns = 1
    while not done.called() and turns < MAXIMUM_WORK_TURNS do
        agent{message = "Continue with the next step of the skill. Call done when the work is finished."}
        turns = turns + 1
    end
    local report = agent{message = "Report the results of this work as the structured output.", tools = {}}
    local attempts = 1
    while report.output == nil and attempts < MAXIMUM_REPORT_ATTEMPTS do
        report = agent{message = "Your last reply had no structured output. Reply with every declared output field now.", tools = {}}
        attempts = attempts + 1
    end
    if report.output == nil then
        error("the agent did not return its structured report after " .. attempts .. " attempts")
    end
    return report
end

Procedure {
    input = {
        story = field.string{required = true, description = "Story lineage id"},
        version = field.string{required = true, description = "Id of the version that entered the stage"},
        versionNumber = field.number{default = 0},
        stage = field.string{default = ""},
        runKey = field.string{default = ""},
        automationId = field.string{default = ""},
        hop = field.number{default = 0},
        author_label = field.string{default = "Ruling fact-checker (Tactus)", description = "Name recorded on saved versions"}
    },
    output = {
        version = field.string{required = true},
        hold = field.boolean{required = true},
        reason = field.string{required = true},
        corrections = field.array{required = true},
        unverifiable = field.array{required = true}
    },
    function(input)
        local checked = work_until_done_then_report(ruling_fact_checker, string.format([[
Fact-check story %s, version %s (version number %s), against the opinion named in its front matter or linked reference.
Record any corrected version with author label: %s.
Report the new version id (empty if you saved nothing), every correction, every point you could not verify,
and whether you read the whole opinion (opinion_read).
]], input.story, input.version, tostring(input.versionNumber), input.author_label))

        if not checked.output.opinion_read then
            return {
                version = input.version,
                hold = true,
                reason = "The opinion could not be read, so the draft was not fact-checked.",
                corrections = checked.output.corrections,
                unverifiable = checked.output.unverifiable
            }
        end

        local corrected = checked.output.version ~= nil and checked.output.version ~= ""
        return {
            version = corrected and checked.output.version or input.version,
            hold = false,
            reason = "",
            corrections = checked.output.corrections,
            unverifiable = checked.output.unverifiable
        }
    end
}
