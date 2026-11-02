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
      staticDir: "web",
      reprojectOnDeploy: true,
      edgeDistributionArn: "arn:aws:cloudfront::712236451410:distribution/EHJUVNTK7AFXH",
    },
    stagingBuild: { enabled: false },
    plugins: [
      {
        name: "newsletter",
        siteId: "distinctive",
        siteOrigin: "https://distinctive-mark.com",
        computeRoleArn: "arn:aws:iam::712236451410:role/amplify-app-shell-distinc-AmplifyComputeRoleD988057-XLvPUM0rTdoC",
        sendingDomain: "distinctive-mark.com",
        fromAddress: "newsletter@distinctive-mark.com",
        fromName: "Distinctive Mark",
        instantAlerts: false,
        itemUrlStyle: "directory",
        theme: {
          accent: "#1D3FD8",
          text: "#121417",
          background: "#F7F8FA",
          surface: "#FFFFFF",
          muted: "#4E545C",
          fontFamily: "Inter, system-ui, 'Helvetica Neue', Arial, sans-serif",
        },
        lists: [
          {
            id: "weekly",
            name: "The Docket",
            description: "One email on Monday: the notable TTAB rulings analyzed, every other decision summarized, and the Wire.",
            kind: "roundup",
            schedule: { draft: "cron(0 12 ? * SUN *)", timezone: "America/New_York" },
            issueType: "newsletter_issue",
            archivePath: "/docket/",
          },
          {
            id: "ruling-alerts",
            name: "Ruling alerts",
            description: "A short email when a new ruling is published.",
            kind: "alert",
            rule: { sections: ["rulings"] },
            approval: "admin",
          },
        ],
      },
    ],
    features: {
      consoleResponder: false,
      inboundEmail: false,
      slack: false,
      storageBackups: false,
    },
  },
});
