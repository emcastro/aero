import ast
import inspect
import pathlib
from collections.abc import Sequence
from numbers import Number

import fiona


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


def extract_argument(code: str, function_name: str):
    # Parse le code en un arbre syntaxique
    arbre = ast.parse(code)

    # Parcourt l'arbre pour trouver l'appel à calc_bbox
    for noeud in ast.walk(arbre):
        if isinstance(noeud, ast.Call):
            # Vérifie si la fonction appelée est calc_bbox
            if isinstance(noeud.func, ast.Name) and noeud.func.id == function_name:
                # Le premier argument est noeud.args[0]
                if noeud.args:
                    # Convertit l'AST de l'argument en code source
                    return ast.unparse(noeud.args[0])
    return None


def get_first_arg_source() -> str:
    frame = inspect.currentframe()
    try:
        caller_frame = frame.f_back.f_back  # type: ignore
        frame_info = inspect.getframeinfo(caller_frame)
        source_lines = frame_info.code_context  # type: ignore
        start_lineno = frame_info.lineno  # type: ignore

        # TODO check correctness
        # Accumulate lines until parentheses are balanced
        full_code = ""
        open_parens = 0
        for line in source_lines:
            full_code += line
            open_parens += line.count("(") - line.count(")")
            if open_parens <= 0 and "(" in full_code:
                break

        # # If still unbalanced, read remaining lines from the source file
        if open_parens > 0 and frame_info.filename:
            with open(frame_info.filename) as f:
                all_lines = f.readlines()
            for i in range(start_lineno, len(all_lines)):
                line = all_lines[i]
                full_code += line
                open_parens += line.count("(") - line.count(")")
                if open_parens <= 0:
                    break

        call_line = full_code.strip()
        argument = extract_argument(call_line, "geodump")
        if argument is not None:
            return argument
    finally:
        del frame
    return "<unnkown>"


GEODATA_STORE = {}


def multipoint(points):
    return {"type": "MultiPoint", "coordinates": points}


def geodump(geometry, *suffix_names, **keywords):
    """Dump a geometry to a test file for visualizing test output on a map.

    The generated GeoJSON can be opened in tools like QGIS to inspect the data.

    The text of the `geometry` argument is used as the feature name in the file (along with any `suffix_names`).
    Values passed via keyword arguments are stored as additional properties on the feature.
    """
    test_name = get_test_name()
    geom_name = get_first_arg_source()
    if test_name not in GEODATA_STORE:
        GEODATA_STORE[test_name] = []
    GEODATA_STORE[test_name].append((to_geojson(geometry), geom_name, suffix_names, keywords))
    return geometry


def flush():
    out_dir = pathlib.Path(__file__).resolve().parent.parent / "tests_dataviz"
    out_dir.mkdir(parents=True, exist_ok=True)

    for test_name, records in GEODATA_STORE.items():
        out_path = str(out_dir / f"{test_name}.geojson")

        schema = {"name": "str"}
        for _, _, _, keywords in records:
            for key, value in keywords.items():
                match value:
                    case str():
                        column_type = "str"
                    case int():
                        column_type = "int"
                    case float():
                        column_type = "float"
                    case _:
                        raise TypeError(f"Type of {value} ({type(value)})")
                schema[key] = column_type

        schema = {"geometry": "Unknown", "properties": schema}
        # Ensure every feature has all schema properties (null if missing).
        schema_props = list(schema["properties"].keys())

        with fiona.open(
            out_path,
            mode="w",
            driver="GeoJSON",
            schema=schema,
            crs="EPSG:4326",
        ) as dst:
            for geom, name, suffixes, keywords in records:
                if geom is None:
                    continue
                dst.write(
                    {
                        "geometry": geom,
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


def isnum(value):
    return isinstance(value, Number)


def to_geojson(value):
    match value:
        case None:
            return None
        case {"type": _, "coordinates": _}:
            # Si c'est déjà un dictionnaire GeoJSON valide
            return value
        case [x, y] if isnum(x) and isnum(y):
            # Point : 2 values
            return {"type": "Point", "coordinates": [x, y]}
        case [xmin, ymin, xmax, ymax] if isnum(xmin) and isnum(ymin) and isnum(xmax) and isnum(ymax):
            # Bbox : 4 values
            return {
                "type": "Polygon",
                "coordinates": [[[xmin, ymin], [xmin, ymax], [xmax, ymax], [xmax, ymin], [xmin, ymin]]],
            }
        case _ if isinstance(value, Sequence):
            # Sequence of coordinates: LineString ou Polygon
            coords = []
            for [x, y] in value:
                coords.append([x, y])
            if len(coords) >= 4 and coords[0] == coords[-1]:
                return {"type": "Polygon", "coordinates": [coords]}
            return {"type": "LineString", "coordinates": coords}
        case _:
            raise ValueError(f"Unsupported geometry type: {type(value)}")
