# Distinctive Mark publication

This repository holds only what is specific to Distinctive Mark™ (distinctive-mark.com). The newsroom application, the Amplify Gen 2 backend, the S3 projection engine and the deployment constructs come from the pinned `@anthusai/papyrus` npm package and the `papyrus-newsroom` Python package. Do not copy Papyrus code into this repository. Fix Papyrus in the Papyrus repository and bump the pins.

## Layout

- `papyrus.config.ts`: registers the brand and the backend (`defineSite`). `backend.publication` is the S3 projection: `web/projector.py` renders pages, and the whole `web/` directory is bundled into the content-actions Lambda as `site_static/`.
- `publication/brand.ts`, `publication/theme.css`: the newsroom (CMS) brand. The CMS uses the generic Papyrus theme pack; do not restyle it here unless asked.
- `web/projector.py`: the Papyrus `SiteProjector` for the public site. It decides which pages exist, what each depends on, and renders them through the Papyrus Markus shell.
- `web/distinctive_content.py`: the content model, read from item summaries and front matter (`docs/content-model.md`).
- `web/distinctive_markup.py`: the page chrome, listing pages, sponsor units and signup units, as HTML.
- `web/css/site-theme.css`, `web/assets/`: the public site's look, client script (filters, signup forms, sticky bar, exit-intent slide-in) and icon.
- `web/site-config.json`: publication identity, issue filters, Wire sources, newsletter and sponsor settings.
- `tests/fixtures/sample-content/`: placeholder items in the CMS layout, used only by `bin/build_local_site.py` and the tests. Never import them into the CMS: the live site is rendered from CMS items alone.
- `amplify/`, `amplify.yml`, `infra/`: the CMS app and backend, as for every Papyrus site.

## Workflow

1. Public site: `pip install -r requirements-publication.txt`, then `python3 bin/build_local_site.py` (add `--as-deployed` to hide the placeholder sponsor as the live site does) and serve `web/dist-local`.
2. Tests: `python3 -m unittest discover -s tests`.
3. CMS: `npm ci` then `npm run dev` (runs `papyrus-app sync`, which writes gitignored route shims). It needs a backend's `amplify_outputs.json` (gitignored).
4. Changing the Papyrus version: edit the exact pin in `package.json`, `infra/package.json`, `infra/site.json` and `requirements-publication.txt` together.
5. Never commit secrets, real email addresses, `amplify_outputs.json` or build output.

## Rules

- No line-level comments. Use long, clear names.
- This repository is a generic container and it is public. Sections, editorial missions and policies, classifier guidance and anything about the business model or the sponsor live only in the newsroom's backend data, never in code, seed files, commits or Kanbus. The brand's `corpora/` paths point at files that intentionally do not exist.
- Author content reaches pages only through Markus with raw HTML disabled. Everything else on a page is generated here and escaped.
- Keep listing pages renderable from item summaries alone, so the projection's dependency digests stay correct.
- The newsletter signup forms post to `newsletter.signupEndpoint` in `web/site-config.json`. While it is `null`, forms send readers to `/subscribe/`, and the subscribe page says signups are not open yet. Never fake a successful signup.
- The sponsor in `web/site-config.json` is a placeholder (`isPlaceholder: true`) until a real sponsor is signed.
- Kanbus is the record of work (project key `dist`). Use the `kbs` CLI (`pip install kanbus`); never read or edit the `project/` directory directly. Without a realtime broker, run it with `KANBUS_NO_DAEMON=1 KANBUS_REALTIME_TRANSPORT=none KANBUS_REALTIME_BROKER=off KANBUS_REALTIME_AUTOSTART=false`. The launch epic lists what is built and what remains.
