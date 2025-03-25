#!/bin/bash

set -xeuo pipefail

cd "$(dirname "$0")"/../devdata

TILE_NAME=N49W001

curl https://openmaps.online/eudem_download/eu_4326/arc1/$TILE_NAME.zip -o $TILE_NAME.zip
rm -rf $TILE_NAME
unzip $TILE_NAME.zip
rm -rf $TILE_NAME.zarr
# Creation options (-co) precondition for our Micropython decoder (except BLOCKSIZE)
# They are often default values, but we set them explicitly to avoid future changes
gdal_translate \
        -of Zarr \
        -co "FORMAT=ZARR_V3" \
        -co "CHUNK_MEMORY_LAYOUT=C" \
        -co "DIM_SEPARATOR=/" \
        -co "BLOCKSIZE=200,200" \
        -co "COMPRESS=NONE" \
        $TILE_NAME/$TILE_NAME.HGT $TILE_NAME.zarr

rm -rf $TILE_NAME $TILE_NAME.zip
