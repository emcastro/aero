from microzarr import match_json_template, ZarrError, check_equals, Axis
import os

root = "devdata/N49W001.zarr"
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
X_metadata = match_json_template("xy_zarr.json", "X/zarr.json")
check_equals(X_metadata["dimension_name"], "X", ["X/zarr.json", "dimension_name"])

consume_key("Y")
Y_metadata = match_json_template("xy_zarr.json", "Y/zarr.json")
check_equals(Y_metadata["dimension_name"], "Y", ["Y/zarr.json", "dimension_name"])

if len(groups) != 1:
    raise ZarrError(f"Expected one group, found {len(groups)}: {groups} at path {root}")

[main_group] = groups
alti_metadata = match_json_template("data_zarr.json", f"{main_group}/zarr.json")
chunk_height = alti_metadata["chunk_height"]
chunk_width = alti_metadata["chunk_width"]


print(X_metadata)
print(Y_metadata)
print(main_group)
print(alti_metadata)

##############


x_axis = Axis.from_group(X_metadata)
y_axis = Axis.from_group(Y_metadata)

# Milieu de piste, Carpiquet
x = -0.4561
y = 49.17617


row = y_axis.to_idx(y)
column = x_axis.to_idx(x)

print(f"Row: {row}, Column: {column}")

chunk_id_x = column // chunk_width
chunk_id_y = row // chunk_height
chunk_column = column % chunk_width
chunk_row = row % chunk_height
print(f"-Row: {chunk_id_y} : {chunk_row}, -Column: {chunk_id_x} : {chunk_column}")

import struct

with open(f"{main_group}/c/{chunk_id_y}/{chunk_id_x}", "rb") as file:

    data = memoryview(file.read())

    data_pos = (chunk_width * chunk_row + chunk_column) * 2
    print(data_pos)
    print(struct.unpack("<h", data[data_pos : data_pos + 2]))
    print(data[data_pos] + (data[data_pos + 1] << 8))
