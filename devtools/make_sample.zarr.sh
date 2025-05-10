#!/bin/bash

set -euo pipefail

cd "$(dirname "$0")"/../devdata

# TILE_NAME=N48W001
TILE_NAME=N49W001

OUT_NAME=$TILE_NAME

if [ -f "$TILE_NAME.zip" ]; then
  echo "$TILE_NAME.zip already exists, skipping download."
else
  if curl https://openmaps.online/eudem_download/eu_4326/arc1/$TILE_NAME.zip -o "$TILE_NAME".zip
  then 
    rm -rf "$TILE_NAME"
    unzip "$TILE_NAME".zip || true
  else
    echo "Failed to download $TILE_NAME.zip"    
  fi
fi

rm -rf $OUT_NAME.zarr
rm -f $OUT_NAME.zarr.zip

python ../devtools/convert_to_zarr.py --out $OUT_NAME.zarr $TILE_NAME/*.HGT
       
#   rm -rf "$TILE_NAME" "$TILE_NAME".zip

