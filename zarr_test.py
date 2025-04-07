from microzarr import match_json_template, ZarrError, check_equals
import os
import struct
from array import array
import micropython


root = "devdata/N48W001.zarr"
os.chdir(root)

#############

groups = set(os.listdir("."))


def consume_key(key):
    if key in groups:
        groups.remove(key)
    else:
        raise ZarrError(f"Key {key} not found in data at path {root}")


#############


consume_key("zarr.json")
[] = match_json_template("root_zarr.json", "zarr.json")

consume_key("X")
X_data = match_json_template("xy_zarr.json", "X/zarr.json")
check_equals(X_data["dimension_name"], "X", ["X/zarr.json", "dimension_name"])

consume_key("Y")
Y_data = match_json_template("xy_zarr.json", "Y/zarr.json")
check_equals(Y_data["dimension_name"], "Y", ["Y/zarr.json", "dimension_name"])

if len(groups) != 1:
    raise ZarrError(f"Expected one group, found {len(groups)}: {groups} at path {root}")

[main_group] = groups
meta_data = match_json_template("data_zarr.json", f"{main_group}/zarr.json")

print(X_data)
print(Y_data)
print(main_group)
print(meta_data)

##############

# TODO charge les mapping X et Y
data = X_data
data_name = "X"
# data = Y_data
# data_name = "Y"

assert data["shape"] == data["chunk_shape"]  # If true, only one file in ${data_name}/c


class Axis:
    def __init__(self, values: array[float]):
        self.values = values

    @micropython.native
    def to_idx(self, value: float):
        # Dichotomic search in self.value of nearest value
        low, high = 0, len(self.values) - 1
        while low <= high:
            mid = (low + high) // 2
            if self.values[mid] < value:
                low = mid + 1
            elif self.values[mid] > value:
                high = mid - 1
            else:
                return mid
        return (
            low
            if low < len(self.values)
            and abs(self.values[low] - value) < abs(self.values[high] - value)
            else high
        )


with open(f"{data_name}/c/0", "rb") as file:
    data_array = array("d", struct.unpack(f"<{data["shape"]}d", file.read()))
    y = Axis(data_array)
    print(data_array)
    print(type(data_array))

y_idx = (y.to_idx(-0.008))
print(y_idx)
print(data_array[y_idx-1])
print(data_array[y_idx])
print(data_array[y_idx+1])
