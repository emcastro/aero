#!/bin/bash

set -euo pipefail

cd "$(dirname "$0")"/../devdata

TILE_NAMES=()
for LAT in N{47..49}
do
        for LON in W00{0..3}
        do
                TILE_NAMES+=("${LAT}${LON}")
        done
        for LON in E00{0..1}
        do
                TILE_NAMES+=("${LAT}${LON}")
        done        
done

OUT_NAME=FRnw

for TILE_NAME in "${TILE_NAMES[@]}"
do 
  if [ -f "$TILE_NAME.zip" ]; then
    echo "$TILE_NAME.zip already exists, skipping download."
    continue
  fi

  if curl https://openmaps.online/eudem_download/eu_4326/arc1/$TILE_NAME.zip -o "$TILE_NAME".zip
  then 
    rm -rf "$TILE_NAME"
    unzip "$TILE_NAME".zip || true
  else
    echo "Failed to download $TILE_NAME.zip"    
  fi
done

rm -rf $OUT_NAME.zarr
rm -f $OUT_NAME.zarr.zip

python ../devtools/convert_to_zarr.py --out $OUT_NAME.zarr ./*/*.HGT
       


# for TILE_NAME in "${TILE_NAMES[@]}"
# do
#   rm -rf "$TILE_NAME" "$TILE_NAME".zip
# done
