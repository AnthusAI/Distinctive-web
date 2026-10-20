# Distinctive publication

This repository holds only what is specific to Distinctive™. The newsroom application, the Amplify Gen 2 backend, the S3 projection engine and the deployment constructs come from the pinned `@anthusai/papyrus` npm package and the `papyrus-newsroom` Python package. Do not copy Papyrus code into this repository. Fix Papyrus in the Papyrus repository and bump the pins.

## Layout

- `papyrus.config.ts`: registers the brand and the backend (`defineSite`). `backend.publication` is the S3 projection: `web/projector.py` renders pages, and the whole `web/` directory is bundled into the content-actions Lambda as `site_static/`.
- `publication/brand.ts`, `publication/theme.css`: the newsroom (CMS) brand. The CMS uses the generic Papyrus theme pack; do not restyle it here unless asked.
- `web/projector.py`: the Papyrus `SiteProjector` for the public site. It decides which pages exist, what each depends on, and renders them through the Papyrus Markus shell.
- `web/distinctive_content.py`: the content model, read from item summaries and front matter (`docs/content-model.md`).
- `web/distinctive_markup.py`: the page chrome, listing pages, sponsor units and signup units, as HTML.
- `web/css/site-theme.css`, `web/assets/`: the public site's look, client script (filters, signup forms, sticky bar, exit-intent slide-in) and icon.
- `web/site-config.json`: publication identity, issue filters, Wire sources, newsletter and sponsor settings.
- `sample-content/`: placeholder items in the CMS layout, used by `bin/build_local_site.py` and the tests. Not deployed.
- `corpora/`: newsroom section definitions.
- `amplify/`, `amplify.yml`, `infra/`: the CMS app and backend, as for every Papyrus site.

## Workflow

1. Public site: `pip install -r requirements-publication.txt`, then `python3 bin/build_local_site.py` and serve `web/dist-local`.
2. Tests: `python3 -m unittest discover -s tests`.
3. CMS: `npm ci` then `npm run dev` (runs `papyrus-app sync`, which writes gitignored route shims). It needs a backend's `amplify_outputs.json` (gitignored).
4. Changing the Papyrus version: edit the exact pin in `package.json`, `infra/package.json`, `infra/site.json` and `requirements-publication.txt` together.
5. Never commit secrets, real email addresses, `amplify_outputs.json` or build output.

## Rules

- No line-level comments. Use long, clear names.
- Author content reaches pages only through Markus with raw HTML disabled. Everything else on a page is generated here and escaped.
- Keep listing pages renderable from item summaries alone, so the projection's dependency digests stay correct.
- The newsletter signup forms post to `newsletter.signupEndpoint` in `web/site-config.json`. While it is `null`, forms send readers to `/subscribe/`, and the subscribe page says signups are not open yet. Never fake a successful signup.
- The sponsor in `web/site-config.json` is a placeholder (`isPlaceholder: true`) until a real sponsor is signed.
