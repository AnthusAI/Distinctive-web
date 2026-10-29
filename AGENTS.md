# Distinctive Mark publication

This repository holds only what is specific to Distinctive Mark™ (distinctive-mark.com). The newsroom application, the Amplify Gen 2 backend, the S3 projection engine and the deployment constructs come from the pinned `@anthusai/papyrus` npm package and the `papyrus-newsroom[markus]` Python package (exact pins, currently 5.55.0). Do not copy Papyrus code into this repository. Fix Papyrus in the Papyrus repository and bump the pins.

Procedures run on Tactus. Relevance classification for other monitors comes from Cyclotron; the TTAB monitor uses no Cyclotron.

## Where it runs

- Public site: https://distinctive-mark.com (`www` redirects to the apex). Newsroom (CMS) at `/newsroom`.
- AWS account `papyrus-production`, 712236451410, `us-east-1`.
- Amplify app `d2xke8ygmrzqpp`, branch `main`.
- CloudFront distribution `EHJUVNTK7AFXH`, stack `papyrus-edge-distinctive-mark` (template `infra/edge/distinctive-mark.yaml`). The default behavior is the S3 projection bucket; `/newsroom*`, `/_next/*` and `/api/*` go to the CMS app.
- App-shell stack `amplify-app-shell-distinctive-cms`.
- Route 53 zone `Z0290267H9H3GQTVF6SK`.
- Newsroom GraphQL endpoint: `https://lzc75j6qdjboblirpdtsalilnq.appsync-api.us-east-1.amazonaws.com/graphql`.
- Knowledge corpus `knowledge-corpus-distinctive`.

## Layout

- `papyrus.config.ts`: registers the brand and the backend (`defineSite`). `backend.publication` is the S3 projection: the standard Papyrus front end renders pages from `web/projection.json`, and the whole `web/` directory is bundled into the content-actions Lambda as `site_static/`. It also configures the `newsletter` plugin.
- `publication/brand.ts`, `publication/theme.css`: the newsroom (CMS) brand. The CMS uses the generic Papyrus theme pack; do not restyle it here unless asked.
- `web/projection.json` and `web/hooks.py`: the settings of the standard Papyrus front end (URLs, sections, feeds, sitemap, head) and the one `page_body` hook that composes Distinctive's pages. Papyrus core renders everything else; see its guide "Building a Papyrus static site".
- `web/distinctive_content.py`: the content model, read from item summaries and front matter (`docs/content-model.md`).
- `web/distinctive_markup.py`: the page chrome, listing pages, sponsor units and signup units, as HTML.
- `web/css/site-theme.css`, `web/assets/`: the public site's look, client script (filters, signup forms, sticky bar, exit-intent slide-in) and icon.
- `web/site-config.json`: publication identity, issue filters, Wire sources, newsletter and sponsor settings.
- `.claude/skills/ttab-ruling-analysis/SKILL.md`: how an agent turns a new TTAB decision into a checked draft ruling page. Procedure only; the editorial rules are fetched from the newsroom at run time.
- `.claude/skills/ruling-fact-check/SKILL.md`, `.claude/skills/ruling-copy-edit/SKILL.md`: the procedures of the two stage bots that follow the analysis.
- `procedures/ttab_ruling_analysis.tac`, `procedures/ruling_fact_check.tac`, `procedures/ruling_copy_edit.tac`: the Tactus procedures that run those skills (one `gpt-6-luna` agent each). They save drafts, never change the stage and never publish.
- `tests/`: Python unit tests (`test_projector.py`). `tests/fixtures/sample-content/` holds placeholder items in the CMS layout, used only by `bin/build_local_site.py` and the tests. Never import them into the CMS: the live site is rendered from CMS items alone.
- `bin/build_local_site.py`: renders the fixtures into `web/dist-local/` for a local preview.
- `docs/content-model.md`: what editors fill in for each section.
- `amplify/`, `amplify.yml`, `infra/`, `middleware.ts`, `next.config.mjs`: the CMS app and backend, as for every Papyrus site.
- `.github/workflows/deploy.yml`: CI and deploy on merge.
- `.kanbus.yml`, `project/`: the Kanbus board (project key `dist`).
- `CONTRIBUTING_AGENT.template.md`: the repository's working discipline for agents (work is declared in Kanbus before code).

## Map of the parts

- Standard projector: Papyrus renders the public site from `web/projection.json`; `web/hooks.py` is the only hook. Listing pages must stay renderable from item summaries alone.
- CMS backend and console: Papyrus Amplify app, branded by `publication/brand.ts`, at `/newsroom`.
- Newsletter plugin: configured in `papyrus.config.ts` (see Newsletter).
- Edge: see Edge.
- Monitoring and router, procedure runner, automations: Papyrus infrastructure, not in this repository (see The TTAB flow and Automations).
- Reader-steering plugin (votes, flags, Proposals), GA4 and consent, the shared relevance Cyclotron, the knowledge run, review requests: not configured here. This repository has no GA4 and no reader-steering plugin. Do not document or add them without a Kanbus issue.

## Common tasks

### Run tests

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements-publication.txt
.venv/bin/python -m unittest discover -s tests
```

The TypeScript check CI runs, from a clean checkout:

```bash
npm ci && echo '{}' > amplify_outputs.json && npx papyrus-app sync && npx tsc --noEmit
```

### Preview the public site

```bash
.venv/bin/python bin/build_local_site.py
python3 -m http.server --directory web/dist-local 8080
```

### Run the CMS locally

`npm ci` then `npm run dev` (runs `papyrus-app sync`, which writes gitignored route shims, then serves on port 3001). It needs a backend's `amplify_outputs.json` (gitignored).

### Bump the Papyrus pin

Papyrus releases come from the Papyrus repository through semantic-release.

1. Edit the exact version in `package.json`, `infra/package.json`, `infra/site.json` (`papyrusVersion`) and `requirements-publication.txt` together.
2. Refresh both lock files: `npm install --package-lock-only --ignore-scripts` in the repository root, then again in `infra/`.
3. Run the tests, open a pull request into `main`.

### Deploy

Merging a pull request into `main` is the deploy. The "CI and deploy" workflow runs the TypeScript check and the Python tests, then calls the reusable workflow `AnthusAI/Papyrus/.github/workflows/amplify-deploy.yml@main`, which starts the Amplify job for that commit with GitHub OIDC (role `distinctive-github-deploy`, app `d2xke8ygmrzqpp`). Amplify's own auto-build is off on `main`. The deploy re-projects the site (`reprojectOnDeploy`).

### Change the app-shell stack

The stack `amplify-app-shell-distinctive-cms` changes separately from the merge deploy:

1. Edit `infra/site.json`.
2. `cd infra && npx papyrus-infra synth --site site.json --account 712236451410`
3. Create a CloudFormation change set from `infra/cdk.out/AmplifyAppShell-distinctive.template.json`, review it, and execute it.
4. The Amplify branch picks up environment changes on its next build.

### Change the edge stack

`infra/edge/distinctive-mark.yaml` is a hand-maintained template. Change it only through a reviewed change set. `infra/README.md` has the first-time order of operations. Never connect the repository from the Amplify console on an app that already has branches: it can delete the branches and their backends.

### Register the ruling procedures

Do this after changing a procedure under `procedures/` or its skill. From the repository root:

```bash
eval "$(aws configure export-credentials --profile papyrus-production --format env)"
export AWS_REGION=us-east-1 PAPYRUS_BACKEND=cloud PAPYRUS_GRAPHQL_AUTH=iam
export PAPYRUS_GRAPHQL_ENDPOINT=https://lzc75j6qdjboblirpdtsalilnq.appsync-api.us-east-1.amazonaws.com/graphql
.venv/bin/papyrus procedures register --file procedures/ttab_ruling_analysis.tac --key distinctive.ttab.ruling-analysis
.venv/bin/papyrus procedures register --file procedures/ruling_fact_check.tac --key distinctive.ruling.fact-check
.venv/bin/papyrus procedures register --file procedures/ruling_copy_edit.tac --key distinctive.ruling.copy-edit
```

Add `--dry-run --json` to preview. The newsroom's published procedures are what the runner executes.

To run the procedure by hand from the repository root (needs Tactus with plugin module support, AnthusAI/Tactus#115, and the Papyrus procedure tools, AnthusAI/Papyrus#456):

```bash
tactus run procedures/ttab_ruling_analysis.tac --no-sandbox --real-all --param proceeding=... --param opinion_url=...
```

It saves drafts and never publishes. The stage bots take `--param story=... --param version=...` instead.

### Create an automation

```bash
.venv/bin/papyrus automations create --id distinctive.ttab --title "Analyze new TTAB rulings" --monitor ttab --publication distinctive --procedure distinctive.ttab.ruling-analysis --input '{"proceeding":"{sourceIdPrefix}","opinion_url":"{documentUrl}"}'
```

Use the same backend environment as for registering a procedure. Other subcommands: `list`, `show`, `runs`, `update`.

## The TTAB flow, end to end

It lives in Papyrus's `papyrus-monitoring` and `papyrus-procedure-runner` stacks, not in this repository.

1. Monitor `MONITOR#ttab` collects TTAB Reading Room final decisions daily, over a 30-day window plus a 180-day recheck for precedential decisions. Matching uses aliases, so a decision is never delivered twice.
2. The router (direct decisions, hourly) delivers each new decision as a pending Reference in Distinctive's newsroom.
3. For a newly created Reference, the router's `procedureTriggers` write a `TRIGGER#` row once and start the procedure runner asynchronously, with input `{proceeding: "{sourceIdPrefix}", opinion_url: "{documentUrl}"}`.
4. The runner executes the newsroom's published procedure `distinctive.ttab.ruling-analysis`: `procedures/ttab_ruling_analysis.tac` plus the skill in `.claude/skills/ttab-ruling-analysis/`. It is analyst only (one `gpt-6-luna` agent): it creates the ruling story in section `rulings` directly at stage `reporting` and never publishes.
5. The stage bots then move the story along. Each takes `{story, version, versionNumber, stage, runKey, automationId, hop}` and returns `{version}`, or `{hold, reason}` to stop the story and raise a review request. Procedures never change the stage and never publish; the engine moves the stage after a successful run that returned a version and did not hold.
   - Entering `reporting`: `distinctive.ruling.fact-check` (`procedures/ruling_fact_check.tac`, skill `.claude/skills/ruling-fact-check`) checks the draft against the opinion and holds if the opinion could not be read.
   - Then `copywriting`: `distinctive.ruling.copy-edit` (`procedures/ruling_copy_edit.tac`, skill `.claude/skills/ruling-copy-edit`) runs the editorial checks (`papyrus_check_story_version`, Papyrus #675) and holds if a fix would change a legal fact.
   - Then `typesetting`: the editor gate. An editor reviews the story in the newsroom and publishes.
6. Planned automation records, waiting on the Papyrus release with story-state triggers (PPY-f0914799): `ruling-analysis` on the TTAB monitor, fact-check on reporting to copywriting, copy-edit on copywriting to typesetting.

## Automations

Available from Papyrus 5.32.0 (epic PPY-9ff95b).

- The record `distinctive.ttab` ("Analyze new TTAB rulings") mirrors the router trigger.
- CLI: `papyrus automations list|show|runs|create|update`. Console: Administration → Automation.
- `maxConcurrent` stays 1 on purpose: about one decision a day, runs of roughly 3 minutes, predictable model cost and no concurrent writes to the newsroom. Extra decisions in a batch start on later router runs.
- In 5.32.0, "enabled" and the limits are display only. Papyrus #639 (in progress) makes enabled and the limits real and adds cost and "run now". That is planned, not live.
- This repository and its session are the test site for the Papyrus automation epic PPY-9ff95b. Papyrus builds the core, and Distinctive tests it and configures the Distinctive side.

## Newsletter

- The Papyrus `newsletter` plugin is configured in `papyrus.config.ts`: SES on `distinctive-mark.com`, from "Distinctive Mark" <newsletter@distinctive-mark.com>.
- List `weekly`, The Docket: drafted Sunday 12:00 ET; an admin approves each issue for a send time, planned as Monday 7:00 ET; sent issues are archived at `/docket/`.
- List `ruling-alerts`: one email per newly published ruling, approved by an admin.
- The signup forms post to `newsletter.signupEndpoint` in `web/site-config.json`, currently `/api/newsletter/subscribe`, with double opt-in. Every email has a one-click unsubscribe. If the endpoint is ever `null`, forms send readers to `/subscribe/`, and the subscribe page says signups are not open yet. Never fake a successful signup.
- Test only with SES mailbox simulator addresses such as `success@simulator.amazonses.com`.
- `cms.siteOrigin` in `infra/site.json` sets `PAPYRUS_SITE_ORIGIN`; without it the newsletter routes answer 503.

## Edge

The distribution has no CustomErrorResponses. An origin-response Lambda@Edge function (NotFoundPage) on the default behavior serves `/404.html` for S3 misses, so `/api/*` statuses from the CMS pass through unchanged (Papyrus #560, applied 2026-10-22).

## Hard rules

- No line-level comments. Use long, clear names.
- This repository is public and its code is a generic container. Sections, editorial missions and policies and classifier guidance live only in the newsroom's backend data, never in code or seed files. Plans, research and roadmap ideas belong in Kanbus issues and the Kanbus wiki as usual.
- Competing publications are never cited as sources or described as data sources. Never record the sponsor's client matters anywhere in the repository.
- Author content reaches pages only through Markus with raw HTML disabled. Everything else on a page is generated here and escaped.
- Keep listing pages renderable from item summaries alone, so the projection's dependency digests stay correct.
- The sponsor in `web/site-config.json` is a placeholder (`isPlaceholder: true`) until a real sponsor is signed. Its units show on the live site anyway (`showWhilePlaceholder: true`), labeled as a placeholder, because driving readers to the sponsor is the site's purpose.
- Never commit secrets, real email addresses, `amplify_outputs.json` or build output. Secrets go in SSM SecureString, never in the repository. Examples use `success@simulator.amazonses.com`.
- Shared checkouts: never switch branches and never `git stash`. Use `git worktree add` for a new branch.
- Main-only flow: branch from `origin/main`, open a pull request into `main`. Merging deploys to production.
- The `.claude/skills/ttab-ruling-analysis` skill and the procedure save drafts only. Human review is never a story state; an editor approves and publishes in the newsroom.
- Kanbus is the record of work (project key `dist`). Use the `kbs` CLI (`pip install kanbus`); never read or edit the `project/` directory directly. Without a realtime broker, run it with `KANBUS_NO_DAEMON=1 KANBUS_REALTIME_TRANSPORT=none KANBUS_REALTIME_BROKER=off KANBUS_REALTIME_AUTOSTART=false`. Issues move open → in_progress → blocked or done. The launch epic lists what is built and what remains.

## Ownership and coordination

- The Papyrus implementation session owns the engine and the shared infrastructure: `papyrus-monitoring` and its router, `papyrus-procedure-runner`, and the Papyrus releases.
- The Cyclotron session owns the relevance lab.
- Tell them before changing shared infrastructure.
- This repository's session owns Distinctive's config, content model, front end and its Kanbus board (project key `dist`).
- Distinctive uses its own Cyclotrons, never the shared one. Policies go into newsroom Administration, not into this repository.

## Current state (2026-10-23)

Live:

- Public site and newsroom at distinctive-mark.com, deployed on merge to `main`.
- Newsletter: The Docket weekly and ruling alerts.
- TTAB monitor, router delivery and the `distinctive.ttab` automation drafting ruling stories for editors.
- NotFoundPage edge function.
- TTAB is the only source monitor.

In progress (Kanbus epics, project `dist`): "Launch Distinctive: public site on Markus and the Papyrus newsroom CMS" and "M1 TTAB decisions monitor". Open epics, not started, cover the knowledge base (corpus, data feature, investigations), rules and court monitors, international and press feeds, and scheduled searches. Run `kbs list --type epic` for the current list.

Known gaps:

- References created by the monitor have a source link that returns 404 (Papyrus PPY-401430).
- The procedure can't run editorial checks itself (PPY-aa63ae).
- The procedure isn't told about an existing story for the same decision (planned in PPY-9ff95b's duplicate checks).
- Notability rating with Distinctive's own Cyclotron is not built (dist-e70efd).
- A reused Reference is not updated when its decision is redesignated (dist-8c0a26).

## Where the docs live

- `README.md`: short orientation.
- `docs/content-model.md`: front matter fields for each section.
- `infra/README.md`: the CMS app stack and the edge stack.
- Papyrus guides (in the Papyrus repository), for example "Building a Papyrus static site" and `docs/site-hosting.md`.
- The Kanbus board: project key `dist`, via `kbs`.
