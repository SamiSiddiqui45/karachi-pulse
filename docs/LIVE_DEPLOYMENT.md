# Live deployment record

Public application: **https://main.d1tsz0y1oa0yn.amplifyapp.com**

Deployment: AWS Amplify Hosting, `ap-south-1`, application `d1tsz0y1oa0yn`, branch `main`. The tested static production bundle was uploaded through the Amplify manual-deployment API. GitHub is not automatically connected to Amplify; publishing a Git commit does not trigger a deployment in this configuration.

## Real AWS integrations

- **Amazon Location Service:** named map `karachi-pulse`, `VectorEsriDarkGrayCanvas`. Browser requests to the actual AWS style/tiles endpoint have been observed successfully. The restricted public key permits only map rendering on this exact map, with the Amplify and local-test origins. Key expiry: **28 January 2027 UTC**. Rotate the key and redeploy before that date to maintain map rendering.
- **Amazon S3:** dedicated private project bucket with all public-access blocks, ACLs disabled, SSE-S3, versioning, HTTPS-only policy and exact-origin CORS. The processed GeoJSON was uploaded under a content-addressed key. Authenticated and signed browser-compatible reads were verified against its SHA-256. Production assets consume a byte-verified S3 snapshot at build time; no expiring S3 URL is embedded in the public app.
- **Amplify Hosting:** static `dist` archive, containing real map configuration and data; no AWS account credentials are shipped to the browser.

The deployment helper is `infrastructure/deploy_aws.py`. Its per-account state is intentionally stored in ignored `.tools/deployment-state.json`; the public map key lives only in ignored `.env.local` and the intended browser build. Never commit AWS secrets, signed upload URLs or session credentials.

## Repeat deployment

```powershell
aws login --profile karachi-pulse --region ap-south-1
python infrastructure/deploy_aws.py prepare
cd frontend
npm ci
npm test
npm run lint
npm run build
$env:PULSE_AWS='1'
$env:PULSE_PREVIEW='1'
npx playwright test
cd ..
python infrastructure/deploy_aws.py publish
python infrastructure/deploy_aws.py status
```

Run public-site verification from `frontend` after deployment completes:

```powershell
$env:PULSE_AWS='1'
$env:PULSE_BASE_URL='https://main.d1tsz0y1oa0yn.amplifyapp.com'
npx playwright test
```

Do not rerun `prepare` on another computer without first inspecting the existing resources and restoring the intended project state; the helper refuses to adopt pre-existing resources blindly. No delete operation is included. Hosting, map requests, S3 storage/versions and data transfer can incur normal AWS charges; see `COSTS.md`.
