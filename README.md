# Aero

Fun with Zarr v3 (as of QGIS Desktop) in MicroPython

# Dev data

- This project includes tools to work with Zarr v3 format. For example, the `devtools/make_sample.zarr.sh` script downloads a sample DEM tile from OpenDEM/OpenMaps and converts it to GeoZarr.

# Rationale

- Data MUST be encoded in Zarr v3 format using GDAL.
- Zarr format is useful because it is:
  - Chunked
  - Reasonably simple
  - Easy to audit using GDAL

# References

- https://docs.micropython.org/en/latest/library/index.html
- https://zarr-specs.readthedocs.io/en/latest/v3/core/v3.0.html

