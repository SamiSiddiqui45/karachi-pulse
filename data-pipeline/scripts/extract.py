"""Download and hash public sources. AWS is never required."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import requests
ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    "health_facilities.csv": "https://huggingface.co/datasets/opendoc-pakistan/pakistan_health_facility_registry/resolve/ebd7bf77bc10243be1bf8914217aea4f11a2ab62/data/processed/health_facilities.csv",
    "pakistan-adm2.geojson": "https://github.com/wmgeolab/geoBoundaries/raw/9469f09/releaseData/gbOpen/PAK/ADM2/geoBoundaries-PAK-ADM2.geojson",
}
def extract(refresh=False):
    raw = ROOT / "data/raw"
    raw.mkdir(parents=True, exist_ok=True)
    manifest_path = raw / "manifest.json"
    previous = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    manifest = {}
    for name, url in SOURCES.items():
        path = raw / name
        downloaded = refresh or not path.exists()
        if downloaded:
            response = requests.get(url, timeout=120)
            response.raise_for_status()
            path.write_bytes(response.content)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        prior = previous.get(name, {})
        manifest[name] = {"url":url,"sha256":digest,"retrieved_at": prior.get("retrieved_at") if prior.get("sha256") == digest and not downloaded else datetime.now(timezone.utc).isoformat()}
    manifest_path.write_text(json.dumps(manifest, indent=2))
    return manifest
if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--refresh", action="store_true")
    print(json.dumps(extract(p.parse_args().refresh), indent=2))
