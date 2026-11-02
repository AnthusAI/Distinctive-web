---
name: ttab-ruling-analysis
description: Analyze a new Trademark Trial and Appeal Board decision into a draft Distinctive Mark ruling story, from the opinion on TTABVUE to a saved draft at the reporting stage. Use when a new TTAB decision needs coverage, when the TTAB monitor files one, or when asked to analyze, summarize or write up a Board ruling. Fact checking and copy editing are separate stage bots (ruling-fact-check, ruling-copy-edit). The same document guides Claude Code and the Tactus ruling-analysis procedure.
---

# TTAB ruling analysis

This skill is the analyst's procedure. The editorial rules are not in it: they live in the newsroom and change there. Fetch them at the start of every run and follow them over anything you remember.

The analysis creates the draft story at the reporting stage and stops. Later stage bots take it from there: a fact checker verifies the draft against the opinion, then a copy editor runs the editorial checks and fixes house style. An editor reviews and publishes. Because the draft will be checked by others, record every point you are unsure how to state in your output, and never skip verifying the facts you state against the opinion as you write them.

## Inputs

- A TTABVUE proceeding (for example `91287216`, `Opposition No. 91287216`, `Serial No. 97425137`) or the opinion's URL.
- Optional: a story lineage already on the board for this decision.

## Steps

1. **Check it is new.** Search the board and the published rulings for the proceeding number and the caption (`papyrus stories show`, the rulings tracker). If the decision is already covered, stop and report the existing item.

2. **Load the rules.** Run `papyrus editorial context --section rulings` and read all of it: the publication's mission and policy (including "What we add"), and the rulings section's mission, policy, assignment guidance and kill criteria. The ruling fields are listed under "Front matter" below.

3. **Read the whole opinion first.** Get the PDF from TTABVUE and read every page before writing. Note the slip-opinion page of every fact you may use. Work from the opinion only: no secondary reporting, and no fact, number, name or quotation that is not in it.

4. **Classify.** Record, exactly as the Board states them: caption, proceeding and number, issue and its long form, outcome, precedential status, panel and author, decision date, the marks at issue (mark, serial or registration number, goods or services and class). Then rate notability from 1 to 5 by the section's scale, and flag the cross-border focus (foreign-domiciled party, Madrid designation, §44 filing).

5. **Find the general meaning before writing.**
   - Precedential: write the `precedent` field first. It is the rule the decision sets, in one or two sentences, without party names, general enough to cite as a proposition, with its key limit. Then write a `title` that states that rule.
   - Not precedential: state the pattern or practice lesson the decision shows, and say it is not precedential where that matters. Never present it as setting law.
   - If you cannot state a general meaning honestly, the decision gets a tracker line (`summary` only), not an analysis.

6. **Write the page** in the order the guidance sets: the general meaning first, then its limits and open questions, then what changes in practice for practitioners and for brand owners, then the case as the illustration, with only the detail the lesson needs. Pin-cite every point (`(at 27–28)`, `(slip op. at 1–5)`). Label the editors' opinion as opinion. Write the `summary` (one listing line, rule first), the `dek`, the `ownerTakeaway` (two or three plain sentences, the only place that speaks to the reader as "you") and `guide` (the related Before You File guide, when one exists). Fill every field in the content model.

7. **Save, do not publish.** Create the story in section `rulings` if needed (`papyrus stories create --section rulings`) and give it its address from the caption, lowercase with hyphens, for example `in-re-wemby-corporation` or `cielo-e-terra-v-hoteles-y-vinedos-del-valle-de-guadalupe` (`papyrus stories set-slug`). Then `papyrus stories save-version --story <lineage> --front-matter-file <yml> --body-file <md> --reason <why> --author-label <agent name>`. Register the opinion as a reference (it is found, not duplicated, if it is already registered) and link it to the story as cited (`papyrus stories link-reference`). The saved draft sits at the reporting stage for the fact-check bot; an editor approves every item before publication.


## Front matter

A ruling page is YAML front matter (no `---` lines when saved through the tools) plus a Markus body. Fill these fields:

- `date`: decision date, `YYYY-MM-DD` in quotes.
- `caption`: `In re [Applicant]` or `[Opposer] v. [Applicant]`, as the Board writes it.
- `title`: the headline. For a precedential decision it states the rule; otherwise the lesson.
- `precedent`: precedential decisions only, the rule in one or two sentences without party names.
- `dek`: two or three sentences on why the rule or lesson matters.
- `summary`: one listing line, rule or lesson first.
- `proceeding` and `proceedingNumber`: for example `Ex parte appeal` and `Serial No. 97752244`.
- `issue` (short, for filters, for example `§2(d)`) and `issueLabel` (the long form).
- `outcome`: as the Board states it, for example `Refusal affirmed`.
- `precedential`: `true` or `false`.
- `notability`: 1 to 5.
- `panel`: the judges and the author, for example `Wellington, Allard and Lavache · Opinion by Wellington`.
- `opinionUrl`: the opinion on TTABVUE.
- `whyNotable`: a list of short reasons, each with a pin cite.
- `ownerTakeaway`: two or three plain sentences for brand owners.
- `guide`: the slug of the related Before You File guide, when there is one.
- `tags`: topics, for example the section of the Act and the goods.
- `marks`: `applicant` and `cited`, each with `label`, `number`, `mark` and `goods` (leave `cited` out when no mark was cited).

## Report

End with: the title, the precedent statement or pattern, the notability and why, the story and version ids, and every point in the opinion you were unsure how to state (the fact checker reads this list).

## Never

- Publish, or run the fact check or editorial checks yourself in place of the stage bots.
- Imply that an attorney wrote or reviewed the piece.
- Give advice on a reader's own facts.
- Mock the losing party.
- Copy editorial rules into this skill: change them in the newsroom.
