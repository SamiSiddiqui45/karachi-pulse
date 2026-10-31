import sys
from pathlib import Path
import json
import pandas as pd
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from validate import valid_coordinates, validate_geojson
from transform import transform

BOUNDARY={"type":"FeatureCollection","features":[{"type":"Feature","properties":{},"geometry":{"type":"Polygon","coordinates":[[[66,24],[68,24],[68,26],[66,26],[66,24]]]}}]}
def row(identifier="1",name="Test hospital",lon="67",lat="25",kind="hospital"):
    return {"osm_id":identifier,"name":name,"longitude":lon,"latitude":lat,"facility_type":kind}

@pytest.mark.parametrize("lon,lat,expected",[(67,25,True),(181,25,False),(67,91,False),(None,25,False),("",25,False),(float('nan'),25,False),(float('inf'),25,False)])
def test_coordinates(lon,lat,expected):
    assert valid_coordinates(lon,lat)==expected

def test_rejections_account_for_every_row():
    records,rejected,report=transform(pd.DataFrame([row(),row(),row("2",lon=""),row("3",lon="74")]),BOUNDARY)
    assert len(records)==1
    assert report["extracted"]==4
    assert report["accepted"]+report["rejected"]==4
    assert {r["reason"] for r in rejected}=={"duplicate_identifier","invalid_or_missing_coordinates","outside_karachi_boundary"}

def test_co_located_distinct_facilities_retained_but_exact_duplicate_removed():
    records,_,report=transform(pd.DataFrame([row(),row("2","Different clinic",kind="clinic"),row("3")]),BOUNDARY)
    assert len(records)==2
    assert report["co_located_extra_records_retained"]==1
    assert report["rejection_reasons"]=={"duplicate_name_and_geometry":1}

def test_boundary_edge_is_accepted_and_unknown_category_preserved():
    records,_,_=transform(pd.DataFrame([row(lon="66",kind="laboratory")]),BOUNDARY)
    assert records[0]["category"]=="Laboratory"

def test_holes_excluded():
    boundary=json.loads(json.dumps(BOUNDARY))
    boundary["features"][0]["geometry"]["coordinates"].append([[66.5,24.5],[67.5,24.5],[67.5,25.5],[66.5,25.5],[66.5,24.5]])
    records,_,report=transform(pd.DataFrame([row()]),boundary)
    assert not records
    assert report["rejected"]==1

def test_production_geojson_and_boundary():
    root=Path(__file__).resolve().parents[1]/"data/processed"
    data=json.loads((root/"facilities.geojson").read_text(encoding="utf-8"))
    report=json.loads((root/"quality-report.json").read_text())
    assert validate_geojson(data)
    assert len(data["features"])==report["accepted"]
    from shapely.geometry import shape
    polygon=shape(json.loads((root/"boundary.geojson").read_text())["features"][0]["geometry"])
    assert all(polygon.covers(shape(f["geometry"])) for f in data["features"])

def test_geojson_rejects_duplicate_ids():
    feature={"type":"Feature","id":"1","geometry":{"type":"Point","coordinates":[67,25]},"properties":{}}
    with pytest.raises(ValueError,match="Duplicate"):
        validate_geojson({"type":"FeatureCollection","features":[feature,feature]})
