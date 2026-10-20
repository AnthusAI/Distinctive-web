# Distinctive infrastructure

`site.json` configures the Papyrus Amplify app-shell stack (the CMS app) for this publication. `package.json` pins `@anthusai/papyrus`, which supplies the template.

```bash
npm ci
npx papyrus-infra synth --site site.json
```

Synthesis only prints and writes `cdk.out/`. Deploying is a separate, reviewed step.

## No reader app

The public site is the S3 projection that the CMS backend creates (`backend.publication` in `../papyrus.config.ts`), served by the CloudFront distribution the backend creates with it (`distribution: { create: true }`). `site.json` has no `reader`, so the stack creates no Amplify reader app. Until a domain is chosen the site answers on the distribution's `*.cloudfront.net` name; adding a domain means adding `aliases` and `acm` to `distribution`.
