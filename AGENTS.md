# Distinctive Mark publication

This repository holds only what is specific to Distinctive Mark™ (distinctive-mark.com). The newsroom application, the Amplify Gen 2 backend, the S3 projection engine and the deployment constructs come from the pinned `@anthusai/papyrus` npm package and the `papyrus-newsroom` Python package. Do not copy Papyrus code into this repository. Fix Papyrus in the Papyrus repository and bump the pins.

## Layout

- `papyrus.config.ts`: registers the brand and the backend (`defineSite`). `backend.publication` is the S3 projection: the standard Papyrus front end renders pages from `web/projection.json`, and the whole `web/` directory is bundled into the content-actions Lambda as `site_static/`.
- `publication/brand.ts`, `publication/theme.css`: the newsroom (CMS) brand. The CMS uses the generic Papyrus theme pack; do not restyle it here unless asked.
- `web/projection.json` and `web/hooks.py`: the settings of the standard Papyrus front end (URLs, sections, feeds, sitemap, head) and the one `page_body` hook that composes Distinctive's pages. Papyrus core renders everything else; see its guide "Building a Papyrus static site".
- `web/distinctive_content.py`: the content model, read from item summaries and front matter (`docs/content-model.md`).
- `web/distinctive_markup.py`: the page chrome, listing pages, sponsor units and signup units, as HTML.
- `web/css/site-theme.css`, `web/assets/`: the public site's look, client script (filters, signup forms, sticky bar, exit-intent slide-in) and icon.
- `web/site-config.json`: publication identity, issue filters, Wire sources, newsletter and sponsor settings.
- `.claude/skills/ttab-ruling-analysis/SKILL.md`: how an agent turns a new TTAB decision into a checked draft ruling page. Procedure only; the editorial rules are fetched from the newsroom at run time.
- `procedures/ttab_ruling_analysis.tac`: the Tactus procedure that runs that skill (an analyst agent and a separate fact-checker agent). Run it from the repository root with `tactus run procedures/ttab_ruling_analysis.tac --no-sandbox --real-all --param proceeding=... --param opinion_url=...`. It needs Tactus with plugin module support (AnthusAI/Tactus#115) and the Papyrus procedure tools (AnthusAI/Papyrus#456). It saves drafts and never publishes.
- `tests/fixtures/sample-content/`: placeholder items in the CMS layout, used only by `bin/build_local_site.py` and the tests. Never import them into the CMS: the live site is rendered from CMS items alone.
- `amplify/`, `amplify.yml`, `infra/`: the CMS app and backend, as for every Papyrus site.

## Workflow

1. Public site: `pip install -r requirements-publication.txt`, then `python3 bin/build_local_site.py` and serve `web/dist-local`.
2. Tests: `python3 -m unittest discover -s tests`.
3. CMS: `npm ci` then `npm run dev` (runs `papyrus-app sync`, which writes gitignored route shims). It needs a backend's `amplify_outputs.json` (gitignored).
4. Changing the Papyrus version: edit the exact pin in `package.json`, `infra/package.json`, `infra/site.json` and `requirements-publication.txt` together.
5. Never commit secrets, real email addresses, `amplify_outputs.json` or build output.

## Rules

- No line-level comments. Use long, clear names.
- This repository is public and its code is a generic container. Sections, editorial missions and policies and classifier guidance live only in the newsroom's backend data, never in code or seed files. Plans, research and roadmap ideas belong in Kanbus issues and the Kanbus wiki as usual. Never describe competing publications as data sources, and never record the sponsor's client matters anywhere in the repository.
- Author content reaches pages only through Markus with raw HTML disabled. Everything else on a page is generated here and escaped.
- Keep listing pages renderable from item summaries alone, so the projection's dependency digests stay correct.
- The newsletter signup forms post to `newsletter.signupEndpoint` in `web/site-config.json`. While it is `null`, forms send readers to `/subscribe/`, and the subscribe page says signups are not open yet. Never fake a successful signup.
- The sponsor in `web/site-config.json` is a placeholder (`isPlaceholder: true`) until a real sponsor is signed. Its units show on the live site anyway (`showWhilePlaceholder: true`), labeled as a placeholder, because driving readers to the sponsor is the site's purpose.
- Kanbus is the record of work (project key `dist`). Use the `kbs` CLI (`pip install kanbus`); never read or edit the `project/` directory directly. Without a realtime broker, run it with `KANBUS_NO_DAEMON=1 KANBUS_REALTIME_TRANSPORT=none KANBUS_REALTIME_BROKER=off KANBUS_REALTIME_AUTOSTART=false`. The launch epic lists what is built and what remains.
