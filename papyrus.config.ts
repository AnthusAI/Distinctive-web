import { defineSite } from "@anthusai/papyrus/define-site";
import { distinctiveBrand } from "./publication/brand";

const defaultCognitoDomainPrefix = "papyrus-distinctive-cms";
const defaultRedirectUrls = ["http://localhost:3001/", "https://distinctive-mark.com/"];

function readNonEmptyEnvironmentValue(name: string): string | undefined {
  const value = process.env[name]?.trim();
  return value ? value : undefined;
}

const cognitoDomainPrefixFromEnvironment = readNonEmptyEnvironmentValue("PAPYRUS_COGNITO_DOMAIN_PREFIX");
const redirectUrlsFromEnvironment = readNonEmptyEnvironmentValue("PAPYRUS_OAUTH_REDIRECT_URLS");

export const resolvedAuthConfiguration = {
  cognitoDomainPrefix: cognitoDomainPrefixFromEnvironment ?? defaultCognitoDomainPrefix,
  applyCognitoDomainPrefix: readNonEmptyEnvironmentValue("PAPYRUS_APPLY_COGNITO_DOMAIN_PREFIX") !== "false",
  redirectUrls: redirectUrlsFromEnvironment
    ? redirectUrlsFromEnvironment.split(",").map((url) => url.trim()).filter((url) => url.length > 0)
    : defaultRedirectUrls,
};

export default defineSite({
  brands: [distinctiveBrand],
  defaultBrand: "distinctive",
  backend: {
    brandId: "distinctive",
    auth: resolvedAuthConfiguration,
    publication: {
      kind: "s3-projection",
      projector: "web/projector.py",
      staticDir: "web",
      reprojectOnDeploy: true,
      edgeDistributionArn: "arn:aws:cloudfront::712236451410:distribution/EHJUVNTK7AFXH",
    },
    stagingBuild: { enabled: false },
    features: {
      consoleResponder: false,
      inboundEmail: false,
      slack: false,
      storageBackups: false,
    },
  },
});
