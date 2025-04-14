from array import array
import json
import struct
from macropython import micropython
from microtyping import List

DIR_NAME = __file__.rsplit("/", 1)[0]


class ZarrError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


def read_json_resource(name: str):
    return read_json(f"{DIR_NAME}/{name}")


def read_json(name: str):
    try:
        with open(name, "r", encoding="utf-8") as file:
            return json.load(file)
    except OSError as exp:
        raise ZarrError(f"Could not read JSON file {name}: {exp}") from exp


def check_equals(template, data, path):
    if template != data:
        raise ZarrError(f"Expected {template} but got {data} at path {path}")


def match_json_template(template_name: str, json_filepath: str) -> dict:
    bindings = {}
    template = read_json_resource(template_name)
    data = read_json(json_filepath)

    def parse_and_check(template, data, path: List[str | int]):  # pylint: disable=R0912
        template_type = type(template)
        data_type = type(data)

        # Check if the template is a variable
        if template_type is str and template.startswith("${") and template.endswith("}"):
            var = template[2:-1]
            bindings[var] = data

        # Otherwise, compare the template and data
        elif template_type != data_type:
            raise ZarrError((template, data, path))

        elif template_type is dict:
            # Check if each item of the template is present in the data
            # Additionnal elements are ignored
            for key, value in template.items():
                if key not in data:
                    raise ZarrError(f"Key {key} not found in data at path {path}")
                parse_and_check(value, data[key], path + [key])

        elif template_type is list:
            # Check if each item of the template is present in the data
            # List must be of the same length
            if len(template) != len(data):
                raise ZarrError(f"List length mismatch at path {path}")
            for idx, (template_value, data_value) in enumerate(zip(template, data)):
                parse_and_check(template_value, data_value, path + [idx])

        elif template_type is str:
            check_equals(template, data, path)
        elif template_type is int:
            check_equals(template, data, path)
        elif template_type is float:
            check_equals(template, data, path)
        elif template_type is bool:
            check_equals(template, data, path)
        else:
            raise ZarrError("Invalid JSON")

    parse_and_check(template, data, [json_filepath])

    return bindings


class Axis:
    def __init__(self, values: array[float]):
        assert len(values) > 1
        self.values = values
        self.standard_orientation = self.values[0] <= self.values[-1]

    @staticmethod
    def from_group(metadata):
        # If true, only one file in ${data_name}/c
        assert metadata["shape"] == metadata["chunk_shape"]

        with open(f"{metadata['dimension_name']}/c/0", "rb") as file:
            data_array = array("d", struct.unpack(f"<{metadata['shape']}d", file.read()))
            return Axis(data_array)

    @micropython.native
    def to_idx(self, target_value: float):
        # Binary search in self.value of nearest value
        low, high = 0, len(self.values) - 1
        while low <= high:
            mid = (low + high) // 2
            mid_value = self.values[mid]
            if self.standard_orientation:
                if mid_value < target_value:
                    low = mid + 1
                elif mid_value > target_value:
                    high = mid - 1
                else:
                    return mid
            else:
                if mid_value < target_value:
                    high = mid - 1
                elif mid_value > target_value:
                    low = mid + 1
                else:
                    return mid

        # At this point, high is before low
        assert high + 1 == low

        # Find closest value
        a = abs(self.values[high] - target_value)
        b = abs(self.values[low] - target_value)

        if a < b:
            return high
        else:
            return low

    def __getitem__(self, idx: int):
        return self.values[idx]
