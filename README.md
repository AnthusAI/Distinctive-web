# Distinctive Mark™ — Trademark News & Analysis

Commentary on TTAB decisions, USPTO practice, and the business of marks.

This repository is the publication. It follows the Anth.us shape:

- **CMS**: the stock Papyrus newsroom (`@anthusai/papyrus`, pinned in `package.json`) with the generic Papyrus theme. Editors write commentary, TTAB rulings, Wire items and standing pages there.
- **Public site**: Markus pages projected into an S3 bucket and served by CloudFront. A save in the newsroom re-renders only the pages that depend on the item, within seconds. The standard Papyrus front end renders them from `web/projection.json`, with the page compositions in `web/hooks.py`; the look is `web/css/site-theme.css`.

The design is the "Distinctive™ — Trademark News & Analysis" canvas: home, ruling commentary, the TTAB rulings tracker, the Wire, the newsletter signup page, the sponsor units and the signup touchpoints.

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements-publication.txt
.venv/bin/python bin/build_local_site.py          # tests/fixtures/sample-content -> web/dist-local
python3 -m http.server --directory web/dist-local 8080
.venv/bin/python -m unittest discover -s tests

npm ci && npm run dev                             # the newsroom CMS, against a backend's amplify_outputs.json
```

See [`AGENTS.md`](AGENTS.md) for the layout and [`docs/content-model.md`](docs/content-model.md) for what editors fill in.

---

Built by [Anthus AI Solutions](https://anth.us) on [Papyrus](https://github.com/AnthusAI/Papyrus).
