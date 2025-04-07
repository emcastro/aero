from microzarr import match_json_template, ZarrError
import os

# TODO on reçoit un répertoire, on cherche zarr.json, X, et Y. Puis on regarde le reste,
# il ne doit y avoir qu'un répertoier. On notre le nom. et on check son zarr


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

consume_key("Y")
Y_data = match_json_template("xy_zarr.json", "Y/zarr.json")

if len(groups) != 1:
    raise ZarrError(f"Expected one group, found {len(groups)}: {groups} at path {root}")

[main_group] = groups
meta_data = match_json_template("data_zarr.json", f"{main_group}/zarr.json")

print(X_data)
print(Y_data)
print(main_group)
print(meta_data)
