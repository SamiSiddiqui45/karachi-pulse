from collections import Counter
import pandas as pd
from shapely.geometry import Point, shape
from shapely.ops import unary_union
from validate import valid_coordinates
CATEGORIES = {"hospital":"Hospital","clinic":"Clinic","doctors":"Doctor","pharmacy":"Pharmacy","dentist":"Dentist","health_centre":"Healthcare centre","health_center":"Healthcare centre"}
def transform(frame, boundary):
    area = unary_union([shape(f["geometry"]) for f in boundary["features"]])
    accepted, rejected, seen_ids, seen_exact, geometries = [], [], set(), set(), Counter()
    for index, row in frame.fillna("").iterrows():
        record = {str(k):str(v).strip() for k,v in row.items()}
        lon, lat, identifier = record.get("longitude"),record.get("latitude"),record.get("osm_id","")
        reason = None
        if not valid_coordinates(lon,lat): reason = "invalid_or_missing_coordinates"
        elif not area.covers(Point(float(lon),float(lat))): reason = "outside_karachi_boundary"
        elif not identifier: reason = "missing_source_identifier"
        elif identifier in seen_ids: reason = "duplicate_identifier"
        else:
            geometry = (float(lon),float(lat))
            exact = (record.get("name","").casefold(),geometry)
            if exact in seen_exact: reason = "duplicate_name_and_geometry"
        if reason:
            rejected.append({"row":int(index)+2,"osm_id":identifier,"reason":reason})
            continue
        seen_ids.add(identifier)
        seen_exact.add(exact)
        geometries[geometry] += 1
        kind = record.get("facility_type") or record.get("amenity") or "unclassified"
        accepted.append({"id":identifier,"longitude":float(lon),"latitude":float(lat),"name":record.get("name") or "Unnamed facility","category":CATEGORIES.get(kind,kind.replace("_"," ").capitalize()),"source_type":kind, "address":record.get("address",""),"operator":record.get("operator",""),"beds":record.get("beds",""),"emergency":record.get("emergency",""),"osm_id":identifier,"source_url":"https://huggingface.co/datasets/opendoc-pakistan/pakistan_health_facility_registry"})
    report = {"extracted":len(frame),"accepted":len(accepted),"rejected":len(rejected),"rejection_reasons":dict(Counter(r["reason"] for r in rejected)),"columns":list(frame.columns),"missing_values":{k:int(v) for k,v in frame.replace("",pd.NA).isna().sum().items()},"categories":dict(Counter(r["category"] for r in accepted)),"co_located_extra_records_retained":sum(n-1 for n in geometries.values() if n>1),"unnamed_accepted":sum(r["name"]=="Unnamed facility" for r in accepted),"boundary":"geoBoundaries Karachi ADM2, represented year 2019; not current district subdivisions"}
    if accepted: report["coordinate_extent"]=[min(r["longitude"] for r in accepted),min(r["latitude"] for r in accepted),max(r["longitude"] for r in accepted),max(r["latitude"] for r in accepted)]
    assert report["extracted"] == report["accepted"] + report["rejected"]
    return accepted,rejected,report
