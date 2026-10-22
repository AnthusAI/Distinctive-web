-- Distinctive Mark: TTAB ruling analysis.
--
-- From a Board decision on TTABVUE to a checked draft ruling page waiting for an editor.
-- Both agents follow the ttab-ruling-analysis skill (.claude/skills/ttab-ruling-analysis/SKILL.md),
-- the same document Claude Code uses, and fetch the editorial rules from the newsroom at run time.
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

ruling_fact_checker = Agent {
    provider = "openai",
    model = "gpt-6-luna",
    system_prompt = [[
You are Distinctive Mark's fact checker for TTAB ruling pages. You did not write the draft.
Do step 7 of the ttab-ruling-analysis skill: read the opinion with papyrus_fetch_pdf_text and the
draft with papyrus_story_version (front matter and body of the version you are given), then check every number, date, name, quotation
and pin cite against the opinion. Remove or correct anything the opinion does not support, and
anything that overstates novelty or turns an inference into a holding. If you change anything, save
one corrected version with papyrus_save_story_version and a reason listing each correction.
Never publish. When finished, call done.
]],
    skills = {".claude/skills/ttab-ruling-analysis"},
    skills_mode = "full",
    tools = {"papyrus", done},
    output = {
        version_id = field.string{required = true},
        corrections = field.array{required = true},
        unverifiable = field.array{required = true}
    }
}

local MAXIMUM_WORK_TURNS = 12

local function work_until_done_then_report(agent, first_message)
    done.reset()
    agent{message = first_message}
    local turns = 1
    while not done.called() and turns < MAXIMUM_WORK_TURNS do
        agent{message = "Continue with the next step of the skill. Call done when the work is finished."}
        turns = turns + 1
    end
    return agent{message = "Report the results of this work as the structured output.", tools = {}}
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
        corrections = field.array{required = true},
        unverifiable = field.array{required = true},
        uncertain_points = field.array{required = true},
        editorial_checks = field.string{required = true},
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

Follow the skill. Create the story in the rulings section if none is given, save the draft version, then call done.
Return the story lineage, the saved version id, the title, the precedent statement (or the pattern, for a
non-precedential decision), the notability rating and every point you were unsure how to state.
]], input.proceeding, input.opinion_url, input.story ~= "" and input.story or "none", input.author_label, input.corpus))

        local checked = work_until_done_then_report(ruling_fact_checker, string.format([[
Fact-check the draft of story %s (version %s) against the opinion at %s.
Record any corrected version with author label: %s (fact check).
]], draft.output.story, draft.output.version_id, input.opinion_url, input.author_label))

        return {
            story = draft.output.story,
            version_id = (checked.output.version_id ~= nil and checked.output.version_id ~= "") and checked.output.version_id or draft.output.version_id,
            title = draft.output.title,
            precedent_or_pattern = draft.output.precedent_or_pattern,
            notability = draft.output.notability,
            corrections = checked.output.corrections,
            unverifiable = checked.output.unverifiable,
            uncertain_points = draft.output.uncertain_points,
            editorial_checks = "not run: no procedure tool for the editorial checks yet (PPY-aa63ae)",
            next_step = "An editor reviews the draft in the newsroom; publishing happens only after approval."
        }
    end
}
