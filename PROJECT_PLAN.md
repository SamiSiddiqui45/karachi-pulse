# Karachi Pulse implementation plan
1. Inspect environment and validate public healthcare sources and licensing.
2. Build reproducible boundary-aware Python ETL and audit reports.
3. Build React/MapLibre dashboard with Amazon Location configuration and explicit offline mode.
4. Prepare private S3 upload and Amplify deployment instructions.
5. Run tests, build, lint and document verified results and deployment blockers.

Environment: Node 24/npm 11, Git, bundled Python runtime and GitHub CLI. The project already has a public AWS deployment; the named AWS session needs renewal before updates can be published.

## Execution status

- Completed: source/license research, pinned nationwide CSV and Karachi polygon acquisition, actual record audit, reproducible ETL and GeoJSON exports.
- Completed: React/TypeScript dashboard, map overlays, clusters, heatmap, search/filtering, metadata, nearby distances, analytics, responsive layout and error handling.
- Completed: named Amazon Location map integration code, secure existing-bucket S3 upload code, Amplify build configuration, AWS instructions and cost notes.
- Tested: 13 Python tests, 8 frontend tests, 8 live and 8 local production browser scenarios, TypeScript, production build and lint. Production dependency audit passes; moderate development dependency findings remain documented.
- Completed: architecture, dataset, deployment, attribution, screenshots, submission draft and demo script.
- Verified: public Amplify app and actual Amazon Location styles and tiles. Prior S3 checks are recorded in docs/LIVE_DEPLOYMENT.md.
- Pending: AWS session renewal and deployment of current local fixes, public demo video and eligibility review. See docs/VERIFICATION.md for evidence and limits.
