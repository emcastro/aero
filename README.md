# Aero

Fun with Zarr v3 (as of QGIS Desktop) in MicroPython

# Dev data

- This project includes tools to work with Zarr v3 format. For example, the `devtools/make_sample.zarr.sh` script downloads a sample DEM tile from OpenDEM/OpenMaps and converts it to GeoZarr.

# Rationale

## Zarr v3

- Data MUST be encoded in Zarr v3 format using GDAL.
- Zarr format is useful because it is:
  - Chunked
  - Reasonably simple
  - Easy to audit using GDAL

## Zip
- Chunks are 30 pixels by 30 pixels so that they fit in MicroPython's small memory (100KB)
- Zarr Directory is too big to be comfortable when copying, and waste space
- We store Zarr chucnks in numerical ordre using a Python script, so that we dont
  have to store the whole directory structure in memory
- 

# References

- https://docs.micropython.org/en/latest/library/index.html
- https://zarr-specs.readthedocs.io/en/latest/v3/core/v3.0.html

# Execution on Linux
```bash
micropython -v -X heapsize=103936 zarr_test.py
```