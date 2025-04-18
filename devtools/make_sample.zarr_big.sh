#!/bin/bash

set -xeuo pipefail

cd "$(dirname "$0")"/../devdata

TILE_NAMES=()
for LAT in N{47..50}
do
        for LON in W00{0..3}
        do
                TILE_NAMES+=("${LAT}${LON}")
        done
done

OUT_NAME=FRnw

for TILE_NAME in "${TILE_NAMES[@]}"
do 
  if curl https://openmaps.online/eudem_download/eu_4326/arc1/$TILE_NAME.zip -o "$TILE_NAME".zip
  then 
    rm -rf "$TILE_NAME"
    unzip "$TILE_NAME".zip || true
  else
    echo "Failed to download $TILE_NAME.zip"    
  fi
done

rm -rf $OUT_NAME.zarr
# Creation options (-co) precondition for our Micropython decoder (except BLOCKSIZE)
# They are often default values, but we set them explicitly to avoid future changes
gdal_merge.py \
        -of Zarr \
        -co "FORMAT=ZARR_V3" \
        -co "CHUNK_MEMORY_LAYOUT=C" \
        -co "DIM_SEPARATOR=/" \
        -co "BLOCKSIZE=200,200" \
        -co "COMPRESS=NONE" \
        -o $OUT_NAME.zarr \
        ./*/*.HGT

for TILE_NAME in "${TILE_NAMES[@]}"
do
  rm -rf "$TILE_NAME" "$TILE_NAME".zip
done
