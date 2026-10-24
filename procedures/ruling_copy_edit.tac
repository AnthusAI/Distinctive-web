-- Distinctive Mark: ruling copy edit stage bot.
--
-- Runs when a ruling story enters the copywriting stage. Follows the ruling-copy-edit skill
-- (.claude/skills/ruling-copy-edit/SKILL.md) and fetches the editorial rules from the newsroom at run time.
-- It never changes the stage and never publishes: the engine moves the story on after a successful run
-- that returns a version and does not hold. Run from the repository root so the skill path resolves.

local done = require("tactus.tools.done")

Toolset "papyrus" {
    type = "plugin",
    modules = {"papyrus_newsroom.tactus_tools"}
}

ruling_copy_editor = Agent {
    provider = "openai",
    model = "gpt-6-luna",
    system_prompt = [[
You are Distinctive Mark's copy editor for TTAB ruling pages. The draft is already fact-checked.
Follow the ruling-copy-edit skill step by step. Use the papyrus tools for everything:
papyrus_editorial_context for the rules and house style, papyrus_story_versions and
papyrus_story_version to read the draft, papyrus_check_story_version to run the editorial checks, and
papyrus_save_story_version to record one revision only if something changed. Never change a legal
fact, holding, quotation, pin cite or citation. Never change the stage. Never publish. When finished, call done.
]],
    skills = {".claude/skills/ruling-copy-edit"},
    skills_mode = "full",
    tools = {"papyrus", done},
    output = {
        version = field.string{required = true, description = "Final version id, or an empty string if nothing was saved"},
        remaining_findings = field.array{required = true},
        changed_fact_findings = field.array{required = true, description = "Findings whose fix would change a legal fact, left unfixed"}
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
        author_label = field.string{default = "Ruling copy editor (Tactus)", description = "Name recorded on saved versions"}
    },
    output = {
        version = field.string{required = true},
        hold = field.boolean{required = true},
        reason = field.string{required = true},
        remaining_findings = field.array{required = true}
    },
    function(input)
        local edited = work_until_done_then_report(ruling_copy_editor, string.format([[
Copy-edit story %s, version %s (version number %s).
Record any revision with author label: %s.
Report the final version id (empty if you saved nothing), every finding that remains, and separately every
finding that could only be fixed by changing a legal fact (changed_fact_findings).
]], input.story, input.version, tostring(input.versionNumber), input.author_label))

        local fact_findings = edited.output.changed_fact_findings
        if fact_findings ~= nil and #fact_findings > 0 then
            return {
                version = input.version,
                hold = true,
                reason = "A fix would change a legal fact, so a person decides.",
                remaining_findings = edited.output.remaining_findings
            }
        end

        local changed = edited.output.version ~= nil and edited.output.version ~= ""
        return {
            version = changed and edited.output.version or input.version,
            hold = false,
            reason = "",
            remaining_findings = edited.output.remaining_findings
        }
    end
}
