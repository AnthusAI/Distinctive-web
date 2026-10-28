# Distinctive Mark™

Trademark news and analysis, live at [distinctive-mark.com](https://distinctive-mark.com). The newsroom (CMS) is at `/newsroom`.

This repository holds only what is specific to Distinctive Mark: the brand and backend configuration, the content model, the public front end (page compositions, markup, styles, client script) and the Tactus procedure that drafts TTAB ruling pages. The engine is not here. It comes from [Papyrus](https://github.com/AnthusAI/Papyrus), pinned exactly: the `@anthusai/papyrus` npm package and the `papyrus-newsroom[markus]` Python package, currently `5.50.0`. Procedures run on Tactus. Never copy Papyrus code into this repository; fix it in Papyrus and bump the pins.

## Where it runs

- Public site: `https://distinctive-mark.com` (`www` redirects to the apex), served by CloudFront from an S3 projection of the newsroom's content.
- Newsroom: `https://distinctive-mark.com/newsroom`, an Amplify app (`d2xke8ygmrzqpp`, branch `main`).
- AWS account `papyrus-production` (`712236451410`), region `us-east-1`.
- CloudFront distribution `EHJUVNTK7AFXH` (stack `papyrus-edge-distinctive-mark`). The default behavior is the S3 projection; `/newsroom*`, `/_next/*` and `/api/*` go to the CMS app.

## Quick start

Prerequisites: Python 3.12, Node 22.

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements-publication.txt
.venv/bin/python bin/build_local_site.py
python3 -m http.server --directory web/dist-local 8080
.venv/bin/python -m unittest discover -s tests
```

The local build renders `tests/fixtures/sample-content/` (placeholder items) into `web/dist-local/`. Never commit build output.

The newsroom app needs a backend's `amplify_outputs.json` (gitignored):

```bash
npm ci
npm run dev
```

## How a change ships

Branch from `main`, open a pull request into `main`, merge. The "CI and deploy" workflow (`.github/workflows/deploy.yml`) runs the TypeScript check and the Python tests on every pull request. On a push to `main` it then deploys to Amplify over GitHub OIDC; no AWS keys are stored. Papyrus releases are cut in the Papyrus repository by semantic-release; this repository picks one up by editing the pin (see `AGENTS.md`).

## Where to look next

[`AGENTS.md`](AGENTS.md) is the operating manual: the map of parts, exact commands, hard rules, ownership and current state. [`docs/content-model.md`](docs/content-model.md) is what editors fill in for each section.

Built by [Anthus AI Solutions](https://anth.us) on Papyrus.
