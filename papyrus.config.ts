import { defineSite } from "@anthusai/papyrus/define-site";
import { distinctiveBrand } from "./publication/brand";

const defaultCognitoDomainPrefix = "papyrus-distinctive-cms";
const defaultRedirectUrls = ["http://localhost:3001/"];

function readNonEmptyEnvironmentValue(name: string): string | undefined {
  const value = process.env[name]?.trim();
  return value ? value : undefined;
}

const cognitoDomainPrefixFromEnvironment = readNonEmptyEnvironmentValue("PAPYRUS_COGNITO_DOMAIN_PREFIX");
const redirectUrlsFromEnvironment = readNonEmptyEnvironmentValue("PAPYRUS_OAUTH_REDIRECT_URLS");

export const resolvedAuthConfiguration = {
  cognitoDomainPrefix: cognitoDomainPrefixFromEnvironment ?? defaultCognitoDomainPrefix,
  applyCognitoDomainPrefix: readNonEmptyEnvironmentValue("PAPYRUS_APPLY_COGNITO_DOMAIN_PREFIX") === "true",
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
      distribution: { create: true },
      reprojectOnDeploy: true,
    },
    stagingBuild: { enabled: true },
    features: {
      consoleResponder: false,
      inboundEmail: false,
      slack: false,
      storageBackups: false,
    },
  },
});
