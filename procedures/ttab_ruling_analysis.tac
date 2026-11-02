-- Distinctive Mark: TTAB ruling analysis.
--
-- From a Board decision on TTABVUE to a draft ruling page at the reporting stage.
-- The analyst follows the ttab-ruling-analysis skill (.claude/skills/ttab-ruling-analysis/SKILL.md),
-- the same document Claude Code uses, and fetches the editorial rules from the newsroom at run time.
-- The fact-check and copy-edit stage bots take the story from there.
-- Run from the repository root so the skill path resolves.

local done = require("tactus.tools.done")

Toolset "papyrus" {
    type = "plugin",
    modules = {"papyrus_newsroom.tactus_tools"}
}

ruling_analyst = Agent {
    provider = "openai",
    model = "gpt-6-luna",
    system_prompt = [[
You are Distinctive Mark's TTAB ruling analyst. Follow the ttab-ruling-analysis skill step by step.
Use the papyrus tools for everything: papyrus_editorial_context for the rules, papyrus_fetch_pdf_text
for the opinion, papyrus_create_story and papyrus_save_story_version to record the draft, and
papyrus_find_or_register_source then papyrus_link_story_reference (role cited) for the opinion.
If an existing story is given, save a new version of it instead of creating another. A new story gets
its address from the caption with papyrus_set_story_slug before you save the draft. Read every page of the opinion before writing. Never publish. When the draft is saved, call done.
]],
    skills = {".claude/skills/ttab-ruling-analysis"},
    skills_mode = "full",
    tools = {"papyrus", done},
    output = {
        story = field.string{required = true},
        version_id = field.string{required = true},
        title = field.string{required = true},
        precedent_or_pattern = field.string{required = true},
        notability = field.number{required = true},
        uncertain_points = field.array{required = true}
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
        proceeding = field.string{required = true, description = "TTABVUE proceeding, for example Serial No. 97752244 or Opposition No. 91287216"},
        opinion_url = field.string{required = true, description = "URL of the opinion PDF on TTABVUE"},
        story = field.string{default = "", description = "Existing story lineage for this decision, if one is on the board"},
        author_label = field.string{default = "TTAB ruling analyst (Tactus)", description = "Name recorded on saved versions"},
        corpus = field.string{default = "knowledge-corpus-distinctive", description = "KnowledgeCorpus where the opinion is registered as a reference"}
    },
    output = {
        story = field.string{required = true},
        version_id = field.string{required = true},
        title = field.string{required = true},
        precedent_or_pattern = field.string{required = true},
        notability = field.number{required = true},
        uncertain_points = field.array{required = true},
        next_step = field.string{required = true}
    },
    function(input)
        local draft = work_until_done_then_report(ruling_analyst, string.format([[
Analyze this TTAB decision for Distinctive Mark.

Proceeding: %s
Opinion PDF: %s
Existing story on the board: %s
Record saved versions with author label: %s
Register the opinion as a reference in corpus: %s

Follow the skill. Create the story in the rulings section at stage reporting (pass stage "reporting" explicitly to papyrus_create_story) if none is given, save the draft version, then call done.
Return the story lineage, the saved version id, the title, the precedent statement (or the pattern, for a
non-precedential decision), the notability rating and every point you were unsure how to state.
]], input.proceeding, input.opinion_url, input.story ~= "" and input.story or "none", input.author_label, input.corpus))

        return {
            story = draft.output.story,
            version_id = draft.output.version_id,
            title = draft.output.title,
            precedent_or_pattern = draft.output.precedent_or_pattern,
            notability = draft.output.notability,
            uncertain_points = draft.output.uncertain_points,
            next_step = "The fact-check and copy-edit bots follow, and an editor publishes."
        }
    end
}
