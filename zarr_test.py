import json
from microtyping import List
import microzarr
import sys
import re
from microzarr import read_json, read_json_resource


def check_equals(template, data, path):
    if template != data:
        raise ValueError(f"Expected {template} but got {data} at path {path}")


def parse_zarr_template(template_name: str, path: str) -> dict:
    bindings = {}
    template = read_json_resource(template_name)
    data = read_json(path)

    def parse_and_check(template, data, path: List[str]):
        template_type = type(template)
        data_type = type(data)

        # Check if the template is a variable
        if template_type is str and template.startswith("${") and template.endswith("}"):
            var = template[2:-1]
            bindings[var] = data

        # Otherwise, compare the template and data
        elif template_type != data_type:
            raise ValueError((template, data, path))

        elif template_type is dict:
            # Check if each item of the template is present in the data
            # Additionnal elements are ignored
            for key, value in template.items():
                if key not in data:
                    raise ValueError(f"Key {key} not found in data at path {path}")
                parse_and_check(value, data[key], path + [key])

        elif template_type is list:
            # Check if each item of the template is present in the data
            # List must be of the same length
            if len(template) != len(data):
                raise ValueError(f"List length mismatch at path {path}")
            for template_value, data_value in zip(template, data):
                parse_and_check(template_value, data_value, path + ["[]"])

        elif template_type is str:
            check_equals(template, data, path)
        elif template_type is int:
            check_equals(template, data, path)
        elif template_type is float:
            check_equals(template, data, path)
        elif template_type is bool:
            check_equals(template, data, path)
        else:
            raise ValueError("Invalid JSON")

    parse_and_check(template, data, [path])

    return bindings


print(parse_zarr_template("root_zarr.json", "devdata/N48W001.zarr/zarr.json"))
print(parse_zarr_template("xy_zarr.json", "devdata/N48W001.zarr/X/zarr.json"))
print(parse_zarr_template("xy_zarr.json", "devdata/N48W001.zarr/Y/zarr.json"))
print(parse_zarr_template("data_zarr.json", "devdata/N48W001.zarr/N48W001/zarr.json"))

