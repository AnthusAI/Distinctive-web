# Distinctive infrastructure

`site.json` configures the Papyrus Amplify app-shell stack (the CMS app) for this publication. `package.json` pins `@anthusai/papyrus`, which supplies the template.

```bash
npm ci
npx papyrus-infra synth --site site.json
```

Synthesis only prints and writes `cdk.out/`. Deploying is a separate, reviewed step.

## No reader app; one edge for the site and the newsroom

The public site is the S3 projection that the CMS backend creates (`backend.publication` in `../papyrus.config.ts`). `site.json` has no `reader` and no domain, so the stack creates only the CMS app (`distinctive-cms`) and no Amplify domain association.

`edge/distinctive-mark.yaml` is the CloudFormation stack `papyrus-edge-distinctive-mark`: one CloudFront distribution for `distinctive-mark.com` and `www.distinctive-mark.com`. The default behavior serves the site bucket through origin access control; `/newsroom*`, `/_next/*` and `/api/*` go to the CMS app's `main` branch (`main.<appId>.amplifyapp.com`) uncached, with the viewer's host in `x-forwarded-host`. The brand's `newsroomBasePath` is `/newsroom`.

Order, because the stack needs the bucket and the redirects store the backend creates, and the backend needs the real distribution ARN:

1. Deploy the backend once without `edgeDistributionArn` (first `main` build).
2. Create the edge stack with a change set: `SiteBucketRegionalDomainName`, `RedirectsKeyValueStoreArn` (from the content-actions Lambda's `PAPYRUS_SITE_BUCKET` and `PAPYRUS_REDIRECTS_KVS_ARN`), `CmsAppId`, and `CertificateArn` once the ACM certificate is issued (empty means no aliases).
3. Set `edgeDistributionArn` in `../papyrus.config.ts` to the stack's `DistributionArn` and merge; that build adds the bucket policy and invalidation rights.
4. Point the Route 53 apex and `www` alias records (zone `Z0290267H9H3GQTVF6SK`) at the distribution.

Never connect the repository from the Amplify console on an app that already has branches: it can delete the branches and their backends.
