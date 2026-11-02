---
name: ruling-copy-edit
description: Copy-edit a fact-checked Distinctive Mark ruling story by running the newsroom's editorial checks, fixing the findings and applying house style, and saving a revision. Use when a ruling story enters the copywriting stage or when asked to copy-edit or run the editorial checks on a ruling page. Never changes a legal fact. The same document guides Claude Code and the Tactus copy-edit bot.
---

# Ruling copy edit

This skill is the copy editor's procedure. The editorial rules are not in it: they live in the newsroom and change there. Fetch them at the start of every run and follow them over anything you remember.

When the copy edit is done the story moves to typesetting, where an editor reviews and publishes. Bots never publish.

## Inputs

- A ruling story (lineage) at the copywriting stage, already fact-checked.

## Steps

1. **Read the latest version** with `papyrus_story_versions` and `papyrus_story_version`: front matter and body.

2. **Load the rules.** Call `papyrus_editorial_context` for section `rulings` and read all of it, including the house style.

3. **Run the checks** on the latest version with `papyrus_check_story_version` (pass `version`, the version id). Read its `status`:
   - `checked`: `clean` is true when there are no violations and no reviews. Otherwise `findings` lists each one with its `rule`, `severity`, `status` (`violation` or `review`), `message` and `quote`, the exact text it concerns. The tool gives no positions and no suggested fixes: find each quote in the body and write the fix yourself.
   - `pending`: no result yet. Call it again once with a longer `wait_seconds` (30). If it is still pending, apply house style only and report that the checks did not finish.
   - `skipped`: checks are off for the site. Apply house style only and report the reason.

4. **Fix each violation, consider each review, and apply house style** from the editorial context, with the smallest edits that resolve them. Do not change any legal fact, holding, quotation, pin cite, number, date, name or citation. If a finding can only be fixed by changing one of those, leave the text as it is and report the finding.

5. **Save one revision** with `papyrus_save_story_version`: the full front matter and body, a reason that lists what you changed and why, and the author label you were given. If nothing needed changing, save nothing. Pass the front matter back exactly as you read it, changing only the values you corrected; keep its YAML valid (quote any value that contains a colon). If the save is refused as invalid YAML, fix the YAML and save again.

6. **Check again.** Run `papyrus_check_story_version` on the saved revision's version id. If findings remain that you can fix within step 4's limits, fix them, save once more and check once more. Run the checks at most twice in total.

## Report

End with: the story, the final version id, what you changed, the check results, and every finding that remains (rule, status, quote, and why you left it).

## Never

- Publish.
- Change a legal fact, holding, quotation, pin cite or citation to satisfy a finding.
- Dismiss a finding silently: report every remaining one.
- Copy editorial rules into this skill: change them in the newsroom.
