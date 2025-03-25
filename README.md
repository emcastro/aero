# Aero

Fun with Zarr v3 (as of QGIS Desktop) in MicroPython

# Dev data

- `devtools/geojson2geozarr.py` downloads a sample DEM tile from OpenDEM/OpenMaps and converts it to GeoZarr.

# Rational

- Data MUST be encoding in Zarr v3 format using GDAL.
- Zarr format is usefull because it is :
  - Chuncked
  - Reasonably simple
  - Easy to audit using GDAL
  - https://zarr-specs.readthedocs.io/en/latest/v3/core/v3.0.html