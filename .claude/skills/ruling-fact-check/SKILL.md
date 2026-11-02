---
name: ruling-fact-check
description: Fact-check a draft Distinctive Mark ruling story against the Board's opinion and save a corrected revision. Use when a ruling story enters the reporting stage, after the ttab-ruling-analysis draft is saved, or when asked to verify a ruling page against the opinion. Corrects facts only; it does not restyle. The same document guides Claude Code and the Tactus fact-check bot.
---

# Ruling fact check

This skill is the fact checker's procedure. You did not write the draft. The editorial rules are not in it: they live in the newsroom. Fetch them with `papyrus_editorial_context` (section `rulings`) when you need to know what a claim must be, and follow them over anything you remember.

When the check is done the story moves on to copywriting. Bots never publish.

## Inputs

- A ruling story (lineage) at the reporting stage, and optionally the version id to check.
- Optional: the analyst's list of uncertain points.

## Steps

1. **Read the draft.** List the story's versions with `papyrus_story_versions` and read the latest (or the version given) with `papyrus_story_version`: front matter and body.

2. **Find the opinion.** Take `opinionUrl` from the version's front matter. If it is missing, use the story's linked reference. If you find neither, report that and stop.

3. **Read the whole opinion** with `papyrus_fetch_pdf_text`, every page. Work from the opinion only: no secondary reporting.

4. **Check every factual statement** in the front matter and the body against the opinion:
   - caption, proceeding and proceeding number
   - decision date and any other dates
   - panel and author of the opinion
   - outcome, as the Board states it
   - holdings, and that no inference stands as a holding
   - quotations, word for word
   - pin cites, against the slip-opinion pages
   - precedential status and the `precedent` statement (a precedential decision sets the rule stated; a non-precedential one is not presented as setting law)
   - the marks at issue: mark, serial or registration number, goods or services, class
   - any claim of novelty ("now", "first") that the Board does not make

5. **Fix errors with the smallest change that makes each statement true.** Correct the number, name, date or cite; remove or soften a claim the opinion does not support; restore a quotation exactly. Do not restyle, reorder or rewrite for tone: that is the copy edit's job. A statement you cannot verify either way is left in place and reported, unless it is plainly unsupported, in which case remove it and report the removal.

6. **Save one corrected version**, only if something changed: `papyrus_save_story_version` with the full corrected front matter and body, a reason that lists each correction (what was wrong, what it now says, the opinion page), and the author label you were given. If no correction is needed, save nothing. Pass the front matter back exactly as you read it, changing only the values you corrected; keep its YAML valid (quote any value that contains a colon). If the save is refused as invalid YAML, fix the YAML and save again.

## Report

End with: the story, the version id (the new one, or the one you checked if nothing changed), each correction, and each point you could not verify.

## Never

- Publish.
- Change style, tone or structure beyond what a correction needs.
- Add a fact, number, name or quotation that is not in the opinion.
- Copy editorial rules into this skill: change them in the newsroom.
