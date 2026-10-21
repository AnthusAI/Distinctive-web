# Content model

Every item is written in the newsroom as YAML front matter plus a Markus body. The item's **section** decides what it is. Listings read only front matter, so fill in the fields below; the body is rendered on the item's own page.

## Commentary (section `commentary`)

Page: `/commentary/<slug>/`.

| Field | Meaning |
| --- | --- |
| `title` | Headline |
| `dek` | One- or two-sentence standfirst |
| `kicker` | Topic label, e.g. `Doctrine · Failure to function` |
| `author` | Byline |
| `date` | Publication date (falls back to the publish time) |
| `readMinutes` | Reading time |
| `tags` | Topics; drive "Filed under" and "More on …" |
| `lead` | `true` to lead the front page |
| `ownerTakeaway` | Plain-language takeaway for brand owners, shown in a box above the body |
| `guide` | Slug of the Before You File guide the takeaway links to |

## TTAB rulings (section `rulings`)

Page: `/rulings/<slug>/`. The tracker at `/rulings/` groups the latest eight weeks by week, precedential decisions first; older weeks are on monthly archive pages at `/rulings/archive/<YYYY-MM>/`. Rulings with `notability` 4 or 5 are "notable" and get the analysis treatment.

| Field | Meaning |
| --- | --- |
| `caption` | `In re [Applicant]` or `[Opposer] v. [Applicant]` |
| `title` | Headline for analysis pieces (defaults to the caption) |
| `dek` | Standfirst for analysis pieces |
| `summary` | One-line summary shown in every listing |
| `proceeding`, `proceedingNumber` | e.g. `Ex parte appeal`, `Serial No. 00000000` |
| `issue` | Short issue used by filters, e.g. `§2(d)`, `Genericness` |
| `issueLabel` | Long form, e.g. `Likelihood of confusion, §2(d)` |
| `outcome` | e.g. `Refusal affirmed`, `Opposition sustained` |
| `precedential` | `true` or `false` |
| `precedent` | For a precedential decision: the rule it sets, stated generally in one or two sentences without party names. When present it leads the ruling page, the tracker row (whose headline is then the `title`, which should state the rule) and the front-page cards |
| `notability` | 1 to 5 |
| `tier` | Optional override of how the tracker shows the ruling: `precedential`, `analysis`, `brief` or `line`. By default precedential decisions are `precedential`, notability 4–5 `analysis`, 3 `brief` (shows the `dek` as a paragraph) and 1–2 `line` (one compact line) |
| `date` | Decision date |
| `panel` | Judges and author of the opinion |
| `opinionUrl` | Link to the opinion on TTABVUE |
| `whyNotable` | List of reasons, shown on the tracker's lead card |
| `marks` | `applicant` and `cited`, each with `mark`, `number`, `goods` and optional `label` |
| `author`, `readMinutes`, `tags`, `lead`, `ownerTakeaway`, `guide` | As for commentary |

The newsletter signup box is placed before the body's second `##` section.

## Before You File guides (section `guides`)

Page: `/guides/<slug>/`, listed at `/guides/` grouped by series. Guides are evergreen: update and redate them rather than publishing a new one.

| Field | Meaning |
| --- | --- |
| `title` | Guide title |
| `dek` | One-sentence standfirst |
| `series` | Series heading the guide is listed under |
| `seriesRank` | Order of the series on the index (lower first) |
| `seriesOrder` | Order of the guide within its series |
| `lastReviewed` | Date the guide was last checked against its sources |
| `readMinutes`, `tags` | As for commentary; shared tags link guides to rulings and commentary |

## The Wire (section `wire`)

No page here: each item links to its source.

| Field | Meaning |
| --- | --- |
| `title` | Headline |
| `source` | `USPTO`, `Courts`, `International` or `Press` (the filters; set in `web/site-config.json`) |
| `sourceUrl` | Link to the source |
| `outlet` | Shown as "via …" |
| `take` | Our one-line take |
| `date` | Date of the news |

## Standing pages (no section, type `page`)

Page: `/<slug>/`. `title` plus a Markus body. About, Editorial policy, Sponsorship and similar pages; each one that exists is linked from the footer.

## Aliases

Any item's `aliases` become 301 redirects to its page.
