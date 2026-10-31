# Submission draft

**Project:** Karachi Pulse — Smart City Intelligence Map
**Tagline:** See Karachi Through Data.

Karachi Pulse turns a genuine OpenStreetMap-derived healthcare registry into an auditable city explorer. Users search names and source categories, zoom clustered locations, inspect available facility metadata, explore mapped-record density, discover nearby facilities and compare category distributions. Every displayed aggregate is computed from loaded GeoJSON.

**Original data:** OpenDoc Pakistan’s Pakistan Health Facility Registry on [Hugging Face](https://huggingface.co/datasets/opendoc-pakistan/pakistan_health_facility_registry), derived from Open Data Pakistan / healthsites.io / OpenStreetMap. ODbL 1.0. The actual downloaded CSV contains 2,997 nationwide records. Polygon filtering accepts 1,004 Karachi records and logs every exclusion. GeoBoundaries’ 2019 Karachi polygon defines the study area.

**Display:** MapLibre renders categorized points, clusters, a true point-density heatmap and the study boundary. Name/category/address searches and source category checkboxes update map and charts together. Source IDs and original registry links are preserved. No current-operation or complete-coverage claim is made.

**AWS integration:** Amazon Location Service supplies the managed named-map basemap; real style and tile requests were verified in public-site desktop and mobile tests. Private Amazon S3 stores a reproducible content-addressed processed snapshot, consumed at build time. Amplify Hosting serves the public frontend without exposing account credentials.

**Public live URL:** https://main.d1tsz0y1oa0yn.amplifyapp.com
**Public GitHub URL:** Pending; no remote configured or push performed.
**Demo video:** Pending; [2:40 script](DEMO_SCRIPT.md) prepared.

## Submission gates

- Local app, genuine data, reproducible ETL, tests and production build: completed.
- Real Amazon Location basemap demonstrated: verified in desktop and mobile browser tests. Prior S3 verification is recorded in LIVE_DEPLOYMENT.md; session renewal is needed to rerun it.
- Public application verified. Public GitHub publication: pending authentication; encouraged and optional under the supplied brief.
- Video recorded and reviewed under three minutes: pending.
- Current official challenge rules, eligibility, deadline and exact submission format: pending verification. Research of accessible official Builder Center pages did not establish the full “Weekend Challenge: Map it” terms. The requirements in the user’s brief are treated as the project brief, not as verified official rules.

Before submission, supply a public demo video under three minutes and confirm eligibility and previously unpublished status. Local fixes still require redeployment. No video upload or challenge submission has been performed.
