# Verification report - 31 October 2026

| Check | Result |
|---|---|
| Full pinned-data ETL, freshly downloaded pinned sources | 2,997 rows; 1,004 accepted; 1,993 rejected and accounted for |
| Python pipeline tests | 13 passed |
| Frontend unit/component tests | 8 passed, including malformed/null dataset handling |
| ESLint and TypeScript production build | Passed |
| Production npm audit (`--omit=dev`) | Zero vulnerabilities |
| Full npm audit | 11 moderate development-tool findings through minimatch; see advisory below |
| Local production browser tests | 8 passed across desktop and emulated mobile Edge |
| Public AWS browser tests | 8 passed across desktop and emulated mobile Edge |
| Real Amazon Location integration | Actual AWS style and tile HTTP responses observed on both viewports |
| Explorer | Clusters, search, details, heatmap, category filters, analytics, dataset audit, fit/reset and no horizontal overflow |
| Error paths | Dataset 503 and successful retry; geolocation denial; empty search and reset |
| Export | Downloaded filtered GeoJSON parsed and verified to contain exactly 467 hospitals |
| GitHub CI | [Hosted run passed](https://github.com/SamiSiddiqui45/karachi-pulse/actions/runs/41189068837): Python tests, frontend tests, lint, build and browser tests |

Live app: https://main.d1tsz0y1oa0yn.amplifyapp.com

An initial explorer test used a five-second cluster wait, which failed while AWS tiles were loading. Its readiness wait now allows 30 seconds, consistent with actual network/browser startup. The expanded public-site suite then passed all eight tests. Browser tests use real MapLibre and its worker; component tests mock the map boundary.

Malformed null JSON and null facility records now return useful dataset validation errors. These local code fixes require redeployment before being present on the public site.

## Security audit limitation

The full audit reports moderate development-tool dependency findings associated with [GHSA-g3hv-75wg-m249](https://github.com/advisories/GHSA-g3hv-75wg-m249). The affected tree is ESLint/typescript-eslint. Production dependency audit passes. A forced major-version dependency override was not applied because legacy minimatch callers may depend on its previous API. Recheck supported upstream upgrades before accepting untrusted glob patterns in development tooling.

## Limits

Mobile testing is viewport emulation, not physical iOS Safari. Live GPS, real-world facility operations and exhaustive accessibility testing are not claimed. Prior S3 verification is recorded in LIVE_DEPLOYMENT.md; the AWS session expired during this review, preventing current management API checks and redeployment until reauthentication. GitHub publication completed: https://github.com/SamiSiddiqui45/karachi-pulse . A public demo video and challenge entry have not been created.

## Reproduce

Run Python pytest on data-pipeline/tests, then npm test, npm run lint and npm run build in frontend. Run npm audit --omit=dev and npm audit separately. For the live suite set PULSE_AWS=1 and PULSE_BASE_URL=https://main.d1tsz0y1oa0yn.amplifyapp.com, then run npx playwright test. For local production testing unset PULSE_BASE_URL and set PULSE_PREVIEW=1.
