# Data analysis ideas

Investigations and live data features built on the public sources in [Data sources](data-sources.md). Each can become a recurring story and, where it updates over time, a data page on the site.

## First data feature: precedential TTAB decisions over time

The TTAB designates which of its decisions are precedential (binding on the Board and examining attorneys; TBMP §101.03). A first count from the Reading Room API (2026-10-20, not yet de-duplicated):

| Year | Decisions | Precedential |
| --- | --- | --- |
| 2008–2011 | 508–927 a year | 58–75 a year |
| 2012–2019 | 596–739 a year | 39–49 a year |
| 2020–2023 | 645–785 a year | 52–55 a year |
| 2024 | 659 | 33 |
| 2025 | 718 | 15 |
| 2026 (to about Oct. 8) | 455 | 10 |

Output is steady while precedential designations have fallen sharply. Before publishing: de-duplicate on `documentId`, handle late redesignations, and reconcile with published counts (12 in 2025 and 8 in 2026 to mid-October by other counts). Shape: a chart on a `/data/` page fed by a small JSON file the backend refreshes on schedule.

## Other investigations

- **Refusal affirmance rates by ground and year** (§2(d), §2(e)(1), §2(e)(4), failure to function, genericness, specimen refusals): which refusals stick on appeal, and how that is changing.
- **Examination consistency.** How outcomes vary across examining attorneys for similar applications, in aggregate (the published research found wide divergence). Uses Office actions from TSDR, TTAB appeals and outcomes.
- **Expungement and reexamination outcomes.** The Trademark Modernization Act proceedings for registered marks that were never used or not used when required. Find the petition records and outcomes; compare successful and failed petitions (evidence types, specimen issues, timing) with topic modelling and recursive summarization; turn the findings into a data-driven guide to preparing a strong petition.
- **Data-driven filing guides.** The same method for each kind of filing: Office action responses by refusal type, specimens, oppositions and cancellations, motions. What do filings that succeed have in common?
- **Opposition and cancellation landscape.** Volume by class of goods and services, typical outcomes, time to decision.
- **Cross-border filings.** Outcomes for foreign-domiciled applicants and Madrid designations into the US: common refusals and how they resolve.
- **Fraud enforcement tracker.** Sanctions orders and terminated records over time.