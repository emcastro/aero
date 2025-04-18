import os
from array import array
import json
import struct
from macropython import micropython
from microtyping import List

DIR_NAME = __file__.rsplit("/", 1)[0]


class Zarr:  # pylint: disable=R0902
    """
    Represents a Zarr dataset and provides methods to access its data.

    Internal attributes:
        path (str): Path to the Zarr dataset.
        main_group (str): Name of the main data group.
        chunk_height (int): Height of each data chunk.
        chunk_width (int): Width of each data chunk.
        x_axis (Axis): X-axis metadata and mapping.
        y_axis (Axis): Y-axis metadata and mapping.
        data (bytearray): Preallocated buffer for chunk data.
        data_xy (tuple): Coordinates of the currently loaded chunk.
    """

    def __init__(self, path: str):
        """
        Initializes the Zarr object by analyzing the dataset structure.

        Args:
            path (str): Path to the Zarr dataset.

        Raises:
            ZarrError: If the dataset structure is invalid.
        """
        # Analyze the Zarr structure
        groups = set(os.listdir(path))

        def consume_key(key):
            if key in groups:
                groups.remove(key)
            else:
                raise ZarrError(f"Key {key} not found in data at path {path}")

        # Check zarr type
        consume_key("zarr.json")
        [] = match_json_template("root_zarr.json", f"{path}/zarr.json")

        # Get X axis mapping between column and longitude
        consume_key("X")
        x_metadata = match_json_template("xy_zarr.json", f"{path}/X/zarr.json")
        check_equals(x_metadata["dimension_name"], "X", ["X/zarr.json", "dimension_name"])

        # Get Y axis mapping between row and latitude
        consume_key("Y")
        y_metadata = match_json_template("xy_zarr.json", f"{path}/Y/zarr.json")
        check_equals(y_metadata["dimension_name"], "Y", ["Y/zarr.json", "dimension_name"])

        # Get lone data group
        if len(groups) != 1:
            raise ZarrError(
                f"Expected one group, found {len(groups)}: {groups} at path {path}",
            )
        [main_group] = groups

        # Read data group organization (chunk size, etc.)
        alti_metadata = match_json_template("data_zarr.json", f"{path}/{main_group}/zarr.json")
        chunk_height = alti_metadata["chunk_height"]
        chunk_width = alti_metadata["chunk_width"]

        # Initialize storage:
        # Data are stored in a preallocated bytearray
        # to avoid memory fragmentation
        buffer_size = chunk_height * chunk_width * 2  # Assume data is in unsigned int16
        data = bytearray(buffer_size)

        # Store attributes
        self.path = path
        self.main_group = main_group
        self.chunk_height = chunk_height
        self.chunk_width = chunk_width

        self.x_axis = Axis.from_group(path, x_metadata)  # TODO improve memory allocation
        self.y_axis = Axis.from_group(path, y_metadata)

        self.data = data
        self.data_xy = (None, None)  # Current chunk loaded

    @micropython.native
    def value_at(self, x: float, y: float):
        """
        Retrieves the value at the specified coordinates.

        Args:
            x (float): Longitude.
            y (float): Latitude.

        Returns:
            int: The value at the specified coordinates.
        """
        row = self.y_axis.to_idx(y)
        column = self.x_axis.to_idx(x)

        chunk_width = self.chunk_width
        chunk_height = self.chunk_height

        chunk_id_x = column // chunk_width
        chunk_id_y = row // chunk_height
        chunk_column = column % chunk_width
        chunk_row = row % chunk_height

        self.load_chunk(chunk_id_x, chunk_id_y)

        # Assume data is in unsigned int16
        data_pos = (chunk_width * chunk_row + chunk_column) * 2
        return struct.unpack_from("<h", self.data, data_pos)[0]

    @micropython.native
    def load_chunk(self, chunk_id_x, chunk_id_y):
        """
        Loads the specified chunk into the buffer.

        Args:
            chunk_id_x (int): Chunk ID along the X-axis.
            chunk_id_y (int): Chunk ID along the Y-axis.
        """
        if self.data_xy == (chunk_id_x, chunk_id_y):
            return

        # Load the chunk data into the buffer
        with open(f"{self.path}/{self.main_group}/c/{chunk_id_y}/{chunk_id_x}", "rb") as file:
            file.readinto(self.data)

        # Update the current chunk
        self.data_xy = (chunk_id_x, chunk_id_y)


class ZarrError(Exception):
    """
    Custom exception for Zarr-related errors.
    """

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
    """
    Represents an axis in the Zarr dataset, providing methods for mapping between
    coordinate values and their corresponding indices.

    Attributes:
        values (array[float]): Array of coordinate values along the axis.
        standard_orientation (bool): Indicates whether the axis values are in ascending order.
    """

    def __init__(self, values_path: str):
        self.values = open(values_path, "rb")
        self.values_size = self.values.seek(0, 2)//8
        print("self.values_size", self.values_size)
        # self.values = values
        self.standard_orientation = self[0] <= self[self.values_size - 1]

    @staticmethod
    def from_group(path: str, metadata: dict):
        """
        Creates an Axis instance from the metadata of a Zarr group.

        Args:
            path (str): Path to the Zarr dataset.
            metadata (dict): Metadata containing axis information.

        Returns:
            Axis: An instance of the Axis class.
        """
        # If true, only one file in ${data_name}/c
        assert metadata["shape"] == metadata["chunk_shape"]

        return Axis(f"{path}/{metadata['dimension_name']}/c/0")

    @micropython.native
    def to_idx(self, target_value: float):
        """
        Finds the index of the closest value to the target value on the axis.

        Args:
            target_value (float): The coordinate value to find the index for.

        Returns:
            int: The index of the closest value.
        """
        # Binary search in self.value of nearest value
        low, high = 0, self.values_size - 1
        while low <= high:
            mid = (low + high) // 2
            mid_value = self[mid]
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
        a = abs(self[high] - target_value)
        b = abs(self[low] - target_value)

        if a < b:
            return high
        else:
            return low

    def __getitem__(self, idx: int):
        """
        Retrieves the coordinate value at the specified index.

        Args:
            idx (int): The index of the coordinate value.

        Returns:
            float: The coordinate value at the specified index.
        """
        print("==========",idx )
        self.values.seek(idx * 8)
        data = struct.unpack("<d", self.values.read(8))
        return data[0]
