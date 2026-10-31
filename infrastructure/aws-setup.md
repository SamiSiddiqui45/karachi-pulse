# AWS setup: credentialed operator runbook

**Existing resources are recorded in [LIVE_DEPLOYMENT.md](../docs/LIVE_DEPLOYMENT.md).** Use the existing `karachi-pulse` profile and deployment helper for this app. The manual steps below are for a fresh independent setup; inspect existing resources first. Do not paste secret keys into chat or frontend configuration. Never delete resources or change unrelated existing resources.

## 1. Inspect before creating

```powershell
aws sts get-caller-identity
aws location list-maps --region ap-south-1
aws location list-keys --region ap-south-1 --query "Entries[].KeyName"
aws s3api list-buckets --query "Buckets[].Name"
aws amplify list-apps --region ap-south-1 --query "apps[].{Name:name,Id:appId}"
```

Review current usage and cost settings first. If a proposed name already exists, inspect its ownership/configuration; do not overwrite it. Select an unused map name and globally unique bucket name. Region must match the map and API key. These read operations need the corresponding list/describe permissions.

## 2. Amazon Location named map and restricted key

In the Amazon Location console for `ap-south-1`, create a new map named `karachi-pulse` with `VectorEsriDarkGrayCanvas` (or a supported vector style). The application uses a **named Maps V1 resource**, whose descriptor endpoint remains documented in AWS’s [map rendering guide](https://docs.aws.amazon.com/location/previous/developerguide/maplibre.html). Do not configure a Maps V2 key or use a V2 style URL with this named-map setup.

Equivalent create command after checking names:

```powershell
aws location create-map --region ap-south-1 --map-name karachi-pulse --configuration Style=VectorEsriDarkGrayCanvas --pricing-plan RequestBasedUsage --description "Karachi Pulse healthcare explorer"
aws location describe-map --region ap-south-1 --map-name karachi-pulse
```

Create a map API key in the console with:

- Rendering actions only: `geo:GetMap*`.
- Allowed resource: exact map ARN returned by `describe-map`.
- Allowed referrers: `http://127.0.0.1:5173/*` for local testing; add the exact eventual Amplify HTTPS origin. Remove local referrers from a public-only key.
- Explicit short validity period for the demo; record its expiry and rotate intentionally.

Never use unrestricted wildcard resources or add Places/Routes permissions for this app. Restriction semantics are documented in [API key restrictions](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-properties-location-apikey-apikeyrestrictions.html). Referrer restrictions reduce misuse; they do not make a public browser key secret.

Store values in ignored `frontend/.env.local`:

```dotenv
VITE_AWS_REGION=ap-south-1
VITE_LOCATION_MAP_NAME=karachi-pulse
VITE_LOCATION_API_KEY=YOUR_RESTRICTED_PUBLIC_MAP_KEY
```

Restart Vite. Verify actual streets, labels, navigation and attribution render; check descriptor, tile, sprite and glyph responses in the browser Network panel. A configured value alone is not proof of a working integration. Invalid keys/regions/referrers show a map-provider error. Do not disclose descriptor URLs containing the key in public screenshots.

## 3. Private S3 storage

Create a **new project bucket** in the same region through the S3 console. Use an unused name. Enable all four Block Public Access controls, Bucket owner enforced ownership (ACLs disabled), default SSE-S3 encryption and versioning. Do not add a public-read bucket policy or ACL. Require HTTPS for clients. For production, add a reviewed deny-insecure-transport policy and least-privilege operator permissions; review [S3 security best practices](https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-practices.html).

Set CORS by copying `s3-cors.example.json`, replacing the allowed origins with only your actual application origins. Do this only for the selected project bucket:

```powershell
aws s3api get-public-access-block --bucket YOUR_PROJECT_BUCKET
aws s3api get-bucket-encryption --bucket YOUR_PROJECT_BUCKET
aws s3api get-bucket-ownership-controls --bucket YOUR_PROJECT_BUCKET
aws s3api get-bucket-cors --bucket YOUR_PROJECT_BUCKET
aws s3api put-bucket-cors --bucket YOUR_PROJECT_BUCKET --cors-configuration file://infrastructure/s3-cors.example.json
```

`get-bucket-cors` can legitimately return `NoSuchCORSConfiguration` before setup. Review any existing CORS configuration and preserve rules you need; do not apply this example to an unrelated bucket. CORS is not authorization. Prefer [least privilege](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-management.html): the uploading identity needs bucket inspection, public-access-block read, PutObject only under `karachi-pulse/`, and GetObject on that prefix for signed reads. No delete or public ACL permissions are needed.

Upload after generating the processed data:

```powershell
python data-pipeline/scripts/upload_s3.py --bucket YOUR_PROJECT_BUCKET --expected-owner YOUR_12_DIGIT_ACCOUNT_ID --region ap-south-1
```

The script checks owner and public-access blocks and uses a content-addressed key and `IfNoneMatch="*"`; an existing identical key causes a precondition failure rather than replacement. No other objects are modified. A one-hour GET URL is written to ignored `frontend/.env.s3.local`, not printed. Run `npm run dev -- --mode s3` from frontend and verify the browser data request succeeds against S3. This mode loads `.env.s3.local` alongside `.env.local`. Remove this ignored file when returning to bundled mode.

Use S3 server access logs or CloudTrail data events and CloudWatch request metrics where appropriate; enable encryption for logging destinations, scope data events to this prefix and account for their extra costs. No monitoring infrastructure has been provisioned by this project.

## 4. Amplify

Follow [deployment instructions](../docs/DEPLOYMENT.md). The project needs no server, database, Lambda or NAT gateway. Current AWS credentials and appropriate account permissions are the prerequisites to resource creation and public deployment. No automatic cleanup/deletion script is included.
