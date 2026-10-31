# Dataset and validation

Retrieved **30 October 2026**. Timestamp and SHA-256 hashes are in `quality-report.json`. Retrieval time records acquisition, not when facilities were surveyed. Source claims a July 2026 collection; its underlying OSM observations may be substantially older.

## Source research

| Candidate | Finding / decision |
|---|---|
| Pakistan Open Data portal | [Pakistan Health Sites](https://opendata.com.pk/dataset/pakistan-health-sites) points to healthsites.io/OSM exports. Portal resource metadata does not consistently state a license. Selected the explicitly ODbL documented derivative below and preserved its provenance. |
| Hugging Face | [OpenDoc Pakistan Health Facility Registry](https://huggingface.co/datasets/opendoc-pakistan/pakistan_health_facility_registry) provides downloadable CSV, source lineage and explicit ODbL 1.0 terms. Downloaded and inspected actual rows. Selected. |
| OpenStreetMap / Overpass | [Overpass API](https://wiki.openstreetmap.org/wiki/Overpass_API) could provide fresher records, but a dated, pinned export provides a reproducible baseline without dependence on a live query service. No Overpass freshness claim. |
| Government | [Sindh Bureau of Statistics health statistics](https://sbos.sindh.gov.pk/health-statistics) provides official health statistics; a usable complete coordinate-level Karachi download was not verified. Not used for point records or app counts. |
| AWS Open Data Registry | [Registry](https://registry.opendata.aws/) and [OSM entry](https://registry.opendata.aws/osm/) were researched. No ready-to-use healthcare subset with Karachi metadata was verified. Not used as a source and no AWS-hosted dataset consumption claimed. |

## Selected source

CSV: `data/processed/health_facilities.csv` in the Hugging Face repository. Pinned repository revision: `ebd7bf77bc10243be1bf8914217aea4f11a2ab62`. Original lineage: OpenStreetMap contributors → healthsites.io → Open Data Pakistan → OpenDoc Pakistan → this spatial subset. Full downloaded source documentation is in `research/source-readme.md`.

CSV SHA-256: `22f3c81a6324dde140a4fb5ec2f120a9ccca36f1041c58a8614bf15caf60c8e4`.

Columns inspected: name, facility_type, amenity, speciality, operator, operator_type, beds, emergency, address, operational_status, longitude, latitude, osm_id, source. Optional attributes are preserved when displayed; all source missing-value counts are reported. The pipeline does not publish removed personal identifiers or add contact information.

## Study geography

[geoBoundaries metadata endpoint](https://www.geoboundaries.org/api/current/gbOpen/PAK/ADM2/) identifies `PAK-ADM2-60131773`, represented year **2019**, source geoBoundaries / Wikipedia, original boundary license **Public Domain**. The full returned metadata is saved at `research/boundary-metadata.json`. Source geometry pinned at geoBoundaries commit `9469f09`.

Only features named exactly `Karachi` are selected. Shapely `covers(Point)` tests the actual polygon, including edges and excluding holes. No loose bounding box is used. This historical layer has one Karachi unit, not the current district partition. GeoBoundaries distribution and API attribution requirements are met by naming geoBoundaries in the UI and documentation; see [geoBoundaries API documentation](https://www.geoboundaries.org/api.html).

## Actual audit results

| Measure | Rows |
|---|---:|
| Nationwide extracted | 2,997 |
| Accepted inside Karachi polygon | 1,004 |
| Rejected outside polygon | 1,634 |
| Rejected missing/invalid coordinates | 359 |
| Duplicate IDs / exact name-coordinate duplicates removed | 0 |
| Extra co-located records retained | 0 |
| Accepted records without a name | 5 |

Accepted coordinates extent `[west,south,east,north]`: `[66.913061,24.792673,67.372562,25.041028]`. This is an extent of observations, not the boundary used for filtering.

| Source-derived category | Count |
|---|---:|
| Hospital | 467 |
| Clinic | 305 |
| Pharmacy | 202 |
| Dentist | 11 |
| Doctor | 6 |
| Alternative | 5 |
| Blood donation | 4 |
| Laboratory | 3 |
| Physiotherapist | 1 |

Latitude and longitude are missing in 359 nationwide rows. Nationwide missing names: 125; address: 2,991; beds: all 2,997. Do not infer availability, beds, ownership, service quality or emergency capabilities from category labels. “Verified” here means source/provenance, schema and geography validated, not independently surveyed.

## License and redistribution

Facilities and the derived database remain ODbL 1.0. Attribute **© OpenStreetMap contributors / healthsites.io**, via Open Data Pakistan and OpenDoc Pakistan. Original code has a separate MIT license. Processed GeoJSON, CSV and source revision are supplied so recipients can access the derivative database and reproduce it. Raw nationwide source files are excluded from Git to avoid redundant redistribution. See [DATA_LICENSE.md](../DATA_LICENSE.md) and [OSM copyright](https://www.openstreetmap.org/copyright).

The source `osm_id` lacks an explicit OSM element type. Therefore the app links to the actual source registry instead of guessing whether an ID refers to a node, way or relation. Identifier collision handling is audited; none occurred in the accepted snapshot.
