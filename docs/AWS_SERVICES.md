# AWS services

Public app: https://main.d1tsz0y1oa0yn.amplifyapp.com

| Service | Purpose | Verification |
|---|---|---|
| Amazon Location Service | Named-map basemap beneath MapLibre overlays | Real styles and tiles verified in desktop and mobile public-site browser tests |
| Amazon S3 | Private, content-addressed GeoJSON snapshot | Prior deployment record reports signed and authenticated reads, CORS and SHA-256 checks; session renewal is needed to rerun them |
| Amplify Hosting | Public HTTPS frontend | Existing app passed eight desktop/mobile end-to-end scenarios |

Production bundles the verified build-time S3 snapshot, avoiding expired runtime signed URLs. The recorded map key expires on 28 January 2027 UTC; rotate it and rebuild before then. See [deployment record](LIVE_DEPLOYMENT.md).

The current Amplify app is manually deployed. GitHub pushes do not trigger AWS deployments. Local validation changes are not published until the authenticated deployment completes.
