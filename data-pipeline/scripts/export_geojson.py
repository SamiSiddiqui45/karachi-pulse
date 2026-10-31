import argparse
import json
import pandas as pd
from extract import ROOT,extract
from transform import transform
from validate import validate_geojson
def run(refresh=False):
    manifest=extract(refresh)
    frame=pd.read_csv(ROOT/"data/raw/health_facilities.csv",dtype=str)
    nationwide=json.loads((ROOT/"data/raw/pakistan-adm2.geojson").read_text(encoding="utf-8"))
    boundary={"type":"FeatureCollection","features":[f for f in nationwide["features"] if f["properties"]["shapeName"]=="Karachi"]}
    if not boundary["features"]: raise ValueError("Karachi boundary missing")
    records,rejected,report=transform(frame,boundary)
    if not records: raise ValueError("No Karachi records; investigate source")
    report["provenance"]=manifest
    data={"type":"FeatureCollection","features":[{"type":"Feature","id":r["id"],"geometry":{"type":"Point","coordinates":[r["longitude"],r["latitude"]]},"properties":{k:v for k,v in r.items() if k not in ("longitude","latitude")}} for r in records]}
    validate_geojson(data)
    processed=ROOT/"data/processed"
    public=ROOT.parent/"frontend/public/data"
    for directory in (processed,public):
        directory.mkdir(parents=True,exist_ok=True)
        for name,value in [("facilities.geojson",data),("boundary.geojson",boundary),("quality-report.json",report)]:
            (directory/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding="utf-8")
    pd.DataFrame(rejected).to_csv(processed/"rejected.csv",index=False)
    pd.DataFrame(records).to_csv(processed/"facilities.csv",index=False)
    print(json.dumps(report,indent=2))
    return report
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--refresh",action="store_true")
    run(p.parse_args().refresh)
