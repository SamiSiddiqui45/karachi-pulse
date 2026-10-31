import math
def valid_coordinates(lon, lat):
    try:
        return math.isfinite(float(lon)) and math.isfinite(float(lat)) and -180 <= float(lon) <= 180 and -90 <= float(lat) <= 90
    except (TypeError, ValueError):
        return False
def validate_geojson(data):
    if data.get("type") != "FeatureCollection":
        raise ValueError("Expected FeatureCollection")
    ids = set()
    for f in data["features"]:
        if f.get("type") != "Feature" or f["geometry"]["type"] != "Point":
            raise ValueError("Expected point feature")
        coords = f["geometry"]["coordinates"]
        if len(coords) != 2 or not valid_coordinates(*coords):
            raise ValueError("Invalid coordinates")
        if f["id"] in ids:
            raise ValueError("Duplicate identifier")
        ids.add(f["id"])
    return True
