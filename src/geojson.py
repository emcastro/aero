import json

from microtyping import Dict, List, Tuple


class GeoJsonWrite:
    def __init__(self, filename: str):
        self.file = open(filename, "w")
        self.need_comma = False

    def __enter__(self):
        self.file.write(
            """{
            "type": "FeatureCollection",
            "name": "zones",
            "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
            "features": [
            """
        )
        return self

    def comma(self):
        if self.need_comma:
            self.file.write(",\n")
        else:
            self.need_comma = True

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.write("]}")
        self.file.close()

    def polygon(self, props: Dict, coords: List[Tuple[float, float]]):
        self.comma()
        json.dump(
            {
                "type": "Feature",
                "properties": props,
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [coords],
                },
            },
            self.file,
        )

    def point(self, props: Dict, coord: Tuple[float, float]):
        self.comma()
        json.dump(
            {
                "type": "Feature",
                "properties": props,
                "geometry": {
                    "type": "Point",
                    "coordinates": coord,
                },
            },
            self.file,
        )

