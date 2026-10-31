# Cost awareness

No cloud resources have been created and no spend is claimed. There is no claim that this project is free or covered by account credits. Verify current pricing and your account’s credit eligibility before provisioning:

- [Amazon Location pricing](https://aws.amazon.com/location/pricing/): map rendering generates billable requests; restrict key actions/resources/referrers, set expiry and monitor usage.
- [S3 pricing](https://aws.amazon.com/s3/pricing/): storage, requests, data transfer, version retention and optional monitoring can contribute charges. The chosen design stores a small content-addressed GeoJSON; retain only intended project versions under your own retention policy.
- [Amplify pricing](https://aws.amazon.com/amplify/pricing/): builds, hosting/storage and bandwidth depend on usage and account terms. Avoid needless rebuild loops.
- CloudTrail data events, CloudWatch request metrics and access-log storage may add costs; scope them to the project and set retention.

Create an account budget and alerts before a public demo, then monitor actual charges. A public map key is visible by design; referrer restrictions reduce unintended use but do not cap spend. No monthly numerical estimate is given because traffic volume and current account-specific pricing/credits have not been verified.

Use static frontend hosting, a single named map, private S3 and client-side overlays. No always-on compute or database is needed. Never delete existing resources as a cost-saving action during setup; resource cleanup requires explicit resource identification and user authorization.
