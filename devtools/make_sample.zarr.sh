#!/bin/bash

set -xeuo pipefail

cd "$(dirname "$0")"/../devdata

TILE_NAME=N49W001

curl https://openmaps.online/eudem_download/eu_4326/arc1/$TILE_NAME.zip -o $TILE_NAME.zip
unzip $TILE_NAME.zip
gdal_translate -of Zarr $TILE_NAME/$TILE_NAME.HGT N49W001_zarr
rm -rf $TILE_NAME $TILE_NAME.zip
