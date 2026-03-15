import inspect
import json
import os
import re

import pathlib


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


def geojson(geometry, *names):
    with open("x.txt", "a") as file:
        file.write(get_first_arg_source())
        if names:
            file.write("-")
            file.write("-".join([str(name) for name in names]))
        file.write("\n")

def flush():
    pass
