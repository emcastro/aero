from microzarr import match_json_template, ZarrError, check_equals, Axis
import os

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
X_metadata = match_json_template("xy_zarr.json", "X/zarr.json")
check_equals(X_metadata["dimension_name"], "X", ["X/zarr.json", "dimension_name"])

consume_key("Y")
Y_metadata = match_json_template("xy_zarr.json", "Y/zarr.json")
check_equals(Y_metadata["dimension_name"], "Y", ["Y/zarr.json", "dimension_name"])

if len(groups) != 1:
    raise ZarrError(f"Expected one group, found {len(groups)}: {groups} at path {root}")

[main_group] = groups
alti_metadata = match_json_template("data_zarr.json", f"{main_group}/zarr.json")

print(X_metadata)
print(Y_metadata)
print(main_group)
print(alti_metadata)

##############

# TODO charge les mapping X et Y
# data = X_data
# data_name = "X"




# target = -0.9
# axis = Axis.from_group(X_metadata)
# print(axis.values)
# idx = axis.to_idx(target)
# print(idx)
# print(target)
# print(axis[idx - 1])
# print(axis[idx], "<<<")
# print(axis[idx + 1])

target = 50
axis = Axis.from_group(Y_metadata)
print(axis.values)
idx = axis.to_idx(target)
print(idx)
print(target)
print(axis[idx - 1])
print(axis[idx], "<<<")
print(axis[idx + 1])
