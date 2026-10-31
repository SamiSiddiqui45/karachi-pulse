# Deployment

Existing public AWS app: https://main.d1tsz0y1oa0yn.amplifyapp.com

Amplify Hosting serves the frontend in ap-south-1. The map uses Amazon Location and a build-time private-S3 snapshot. See [deployment record](LIVE_DEPLOYMENT.md) for repeat-deployment commands. Preserve ignored local state; the helper refuses to overwrite unrelated resources.

Renew the `karachi-pulse` AWS profile, run `prepare`, build and test the frontend, then run `publish` and `status` until Amplify returns `SUCCEED`. Finally run browser tests with `PULSE_AWS=1` and `PULSE_BASE_URL` set to the public URL. Local changes are only live after deployment succeeds.

## GitHub and CI

Authenticate the bundled `.tools/gh/bin/gh.exe`, inspect the signed-in account, create the public project repository and push the reviewed source. Environment files, AWS state and credentials are ignored. Processed ODbL data is distributed intentionally with attribution.

`.github/workflows/ci.yml` runs Python tests, frontend tests, lint, build and Edge desktop/mobile browser tests on Windows. Hosted CI execution remains unverified until the first GitHub run succeeds. It does not deploy AWS resources; the existing Amplify app has no automatic GitHub connection.

## Dataset updates

Run the pinned ETL, review provenance and rejection counts, test and rebuild. Never embed short-lived private-S3 URLs in the permanent site. Restrict the browser map key to this project's map and actual app origins. Never include account credentials in frontend configuration.
