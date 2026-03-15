import fiona
import pathlib
import inspect
import re


def get_test_name():
    stack = inspect.stack()
    try:
        for frame_info in stack:
            if frame_info.function.startswith("test_"):
                return frame_info.function
        # Fallback to the immediate caller function name
        if len(stack) >= 3:
            return stack[2].function
    finally:
        # Avoid reference cycles
        del stack
    return "unknown_test"


def get_first_arg_source() -> str:
    frame = inspect.currentframe()
    try:
        # Walk back to the caller of the function that invoked this helper
        caller_frame = frame.f_back.f_back  # type: ignore
        source_lines = inspect.getframeinfo(caller_frame).code_context  # type: ignore
        call_line = "".join(source_lines).strip()  # type: ignore

        # Try to extract the first argument expression from a call like:
        # geojson(point_result)
        matcher = re.search(r"\bgeojson\s*\(\s*([^,\)]+)", call_line)
        if matcher:
            return matcher.group(1).strip()
    finally:
        del frame
    return "<unnkown>"


GEODATA_STORE = {}


def geojson(geometry, *suffix_names, **key_words):
    test_name = get_test_name()
    geom_name = get_first_arg_source()
    if test_name not in GEODATA_STORE:
        GEODATA_STORE[test_name] = []
    GEODATA_STORE[test_name].append((geometry, geom_name, suffix_names, key_words))


def flush():
    out_dir = pathlib.Path(__file__).resolve().parent / "tests_dataviz"
    out_dir.mkdir(parents=True, exist_ok=True)

    for test_name, records in GEODATA_STORE.items():
        out_path = out_dir / f"{test_name}.geojson"

        schema = {"name": "str"}
        for _, _, _, keywords in records:
            for key, value in keywords.items():
                match value:
                    case str():
                        column_type = "str"
                    case int():
                        column_type = "int:20"
                    case float():
                        column_type = "float"
                    case _:
                        raise TypeError(f"Type of {value} ({type(value)})")
                schema[key] = column_type

        schema = {"geometry": "Unknown", "properties": schema}
        # Ensure every feature has all schema properties (null if missing).
        schema_props = list(schema["properties"].keys())

        with fiona.open(
            str(out_path),
            mode="w",
            driver="GeoJSON",
            schema=schema,
            crs="EPSG:4326",
        ) as dst:
            for geom, name, suffixes, keywords in records:
                geo = to_geojson(geom)
                if geo is None:
                    continue
                dst.write(
                    {
                        "geometry": geo,
                        "properties": make_props(name, suffixes, keywords, schema_props),
                    }
                )

    GEODATA_STORE.clear()


def make_props(name, suffixes, keywords, schema_props):
    if suffixes:
        fullname = name + "-" + "-".join(str(s) for s in suffixes)
    else:
        fullname = name

    props = {}
    for key in schema_props:
        if key == "name":
            props[key] = fullname
        else:
            props[key] = keywords.get(key, None)
    return props


def to_geojson(value):
    if value is None:
        return None
    # If already a GeoJSON dict, assume valid
    if isinstance(value, dict) and "type" in value and "coordinates" in value:
        return value
    # Point-like
    if isinstance(value, (list, tuple)) and len(value) == 2 and not isinstance(value[0], (list, tuple)):
        return {"type": "Point", "coordinates": [float(value[0]), float(value[1])]}  # type: ignore
    # Sequence of coordinates: LineString or Polygon
    if isinstance(value, (list, tuple)):
        coords = []
        for v in value:
            if not isinstance(v, (list, tuple)) or len(v) != 2:
                raise ValueError("Unsupported geometry coordinate format")
            coords.append([float(v[0]), float(v[1])])  # type: ignore
        if len(coords) >= 4 and coords[0] == coords[-1]:
            return {"type": "Polygon", "coordinates": [coords]}
        return {"type": "LineString", "coordinates": coords}
    raise ValueError(f"Unsupported geometry type: {type(value)}")
