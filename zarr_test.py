from microzarr import match_json_template


print(match_json_template("root_zarr.json", "devdata/N48W001.zarr/zarr.json"))
print(match_json_template("xy_zarr.json", "devdata/N48W001.zarr/X/zarr.json"))
print(match_json_template("xy_zarr.json", "devdata/N48W001.zarr/Y/zarr.json"))
print(match_json_template("data_zarr.json", "devdata/N48W001.zarr/N48W001/zarr.json"))
