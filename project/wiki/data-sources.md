# Public trademark-law data sources

Government and open legal data the knowledge base and monitors can build on. Court opinions and federal government works are public domain (*Georgia v. Public.Resource.Org*, 2020; 17 U.S.C. §105). Status as of 2026-10-20: **verified** means a live read-only request returned real records; everything else needs a live check before we build on it.

## USPTO

| Source | What it holds | Access | Status |
| --- | --- | --- | --- |
| TTAB Reading Room (`ttab-reading-room.uspto.gov`) | Every TTAB decision since 1986 (about 19,000; about 1,350 precedential): decision date, proceeding type (ex parte appeal, opposition, cancellation, concurrent use), decision type, grounds and issues, outcome, panel and writing judge, examining attorney, parties, marks and goods on each side, opinion PDF | JSON search API behind the official site, no key. `POST /ttab-efoia-api/decision/search`, filter `dateRangeData.decisionDate`, sort `issueDate`, optional `parameterData.precedentCitableIndicator: "Y"`. PDF at `/ttab-document/` + `documentId` (keep the double slash). | **Verified** |
| USPTO Open Data Portal: TTAB daily XML (`TTABTDXF`) | Docket data for TTAB proceedings (filings, decision events); no opinions, no precedential flag | Free API key required | Not verified (needs a key) |
| TSDR (trademark status and documents) | Each application's file history, including Office actions: the examining attorney's reasoning on every refusal | API key, rate-limited | To verify |
| USPTO trademark application bulk data | Daily filings: marks, goods and services, classes, owners | Open Data Portal | To verify |
| USPTO Office of the Chief Economist trademark case files dataset | Research dataset of application histories | Download | To verify |
| USPTO trademark decisions (`data.uspto.gov/tm-decisions`) | Administrative orders, including sanctions against fraudulent filings | Web | To verify |
| Expungement and reexamination proceedings (Trademark Modernization Act, since Dec. 2021) | Petitions, institution decisions and outcomes | To find | To verify |
| Federal Register (USPTO documents) | Proposed and final trademark rules, fee changes | Public JSON API | To verify |

## Courts

| Source | What it holds | Access | Status |
| --- | --- | --- | --- |
| Federal Circuit opinions (`cafc.uscourts.gov`) | Appeals from the TTAB | Web, PDFs | To verify cadence |
| Supreme Court (`supremecourt.gov`) | Dockets, orders, opinions | Web | To verify |
| GovInfo US Courts collection | Federal district, appellate and bankruptcy opinions | API (free api.data.gov key) | To verify |
| CourtListener (Free Law Project) | Millions of opinions; dockets mirrored from PACER (RECAP); nature-of-suit 840 = trademark | Free API and bulk data | Atom feed for TTAB **verified** (precedential decisions) |
| Caselaw Access Project (Harvard) | About 6.7 million published US cases through 2020 | Open bulk data | To verify |
| PACER | Dockets and filings | Paid per page | Use sparingly |

## International (read for US consequences)

WIPO Madrid System notices; EUIPO and the Court of Justice of the EU; INPI France; Latin American offices: IMPI (Mexico), INPI (Brazil), SIC (Colombia), INPI (Argentina), INAPI (Chile). All to verify.

## Caveats

- Opinions are mostly PDFs; text extraction quality varies, especially for older scans.
- Reading Room issue tags come from OCR and pattern matching; treat them as hints. The same decision can appear twice: dedupe on `documentId`. Decisions appear about two weeks after issuance.
- Analysis naming individual examining attorneys or judges needs care before anything is published; publish aggregates.