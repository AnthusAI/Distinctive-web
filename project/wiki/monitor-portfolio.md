# Monitor portfolio

Monitors feed new items into the newsroom as pending references for the Cyclotron and section classifiers. Each entry: what it watches, cadence, the section it mostly feeds, and the Papyrus source type it needs. Papyrus 4.0.0 ships only a Hacker News collector (local worker, JSON config, SQLite checkpoint); everything below needs new source types in Papyrus core.

## Papyrus capabilities needed

1. RSS/Atom source type (Papyrus story PPY-731c23e0).
2. JSON API source type (Federal Register, CourtListener, USPTO APIs).
3. Page-change source type for pages without feeds (close to Papyrus story PPY-5a111e43).
4. Scheduled search source type (Papyrus web search), with query sets and cadences per monitor.
5. TTAB Reading Room adapter: rolling 30-day window, dedupe on `documentId`, precedential re-check over 90–180 days.
6. PDF handling (opinions are PDFs) and stable source ids (e.g. proceeding numbers) instead of URL-only dedupe.
7. Monitor definitions stored as backend data (query sets and cadences are editorial configuration), a hosted scheduler, and routing to this publication's own Cyclotrons.

## Monitors

| Monitor | Cadence | Feeds | Source type |
| --- | --- | --- | --- |
| TTAB decisions (Reading Room) | Daily | Rulings | TTAB adapter |
| TTAB precedential re-check | Daily | Rulings | TTAB adapter |
| Federal Circuit opinions (TTAB appeals, Lanham Act) | Daily | Rulings, Commentary | Page-change or RSS |
| Federal court Lanham Act opinions (CourtListener, nature of suit 840) | Daily | Wire (Courts), Commentary | JSON API |
| Supreme Court trademark grants and opinions | Weekly | Wire, Commentary | Page-change |
| Federal Register: USPTO trademark rules and fees | Daily | Wire (USPTO), Guides | JSON API |
| USPTO news and trademark alerts | Daily | Wire (USPTO) | RSS or page-change |
| USPTO pages: TMEP, examination guides, fee schedule, sanctions orders, scam warnings | Weekly | Wire, Guides | Page-change |
| TTAB announcements and TBMP updates | Weekly | Wire, Commentary | Page-change |
| USITC Section 337 trademark and trade dress; CBP IP enforcement | Weekly | Wire | RSS or page-change |
| WIPO Madrid System notices | Weekly | Wire (International), Guides | RSS or page-change |
| EUIPO, CJEU trademark judgments, INPI France | Weekly | Wire (International) | RSS or page-change |
| Latin American offices (IMPI, INPI Brazil, SIC, INPI Argentina, INAPI) | Weekly | Wire (International) | Page-change |
| Practitioner press feeds | Daily | Wire signals, Commentary ideas | RSS |
| Scheduled searches: daily (TTAB precedential, Lanham Act rulings, USPTO trademark news, trademark scam solicitations) | Daily | Wire signals | Search |
| Scheduled searches: weekly (failure to function, genericness, Madrid in the US, foreign applicants, squatting abroad, marketplace brand programs, filing fraud) | Weekly | Wire signals, Commentary | Search |
| Scheduled searches: monthly guide research | Monthly | Research assignments | Search |

Search and press results are secondary signals: they become Wire items only with a primary source, otherwise they are leads to trace.

## Order

1. TTAB decisions, Federal Register, USPTO news, Federal Circuit opinions, a practitioner press feed, the daily searches.
2. CourtListener, USPTO page monitors, WIPO Madrid.
3. International offices, USITC and CBP, a filing-data watchlist of well-known brands.