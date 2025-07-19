import struct
import json

import click
import rasterio
from rasterio.merge import merge
from typing import List

BLOCKSIZE = 80


@click.command()
@click.option("--out", "-o", help="Output name for the Zarr file.")
@click.argument("sources", nargs=-1)  # Accept multiple tile names as arguments.
def gdal_aero_zarr(out, sources):
    print(f"Converting {sources} into {out}")

    src_files_to_mosaic = [rasterio.open(fp) for fp in sources]
    mosaic, out_trans = merge(src_files_to_mosaic)

    out_meta = src_files_to_mosaic[0].meta.copy()
    out_meta.update(
        {
            "driver": "ZARR",
            "dtype": mosaic.dtype,
            "height": mosaic.shape[1],
            "width": mosaic.shape[2],
            "transform": out_trans,
            "format": "ZARR_V3",
            "blocksize": f"{BLOCKSIZE},{BLOCKSIZE}",
            "compress": "NONE",
            "dim_separator": "/",
        }
    )

    with rasterio.open(f"{out}", "w", **out_meta) as dest:
        dest.write(mosaic)
    
    print("Done")


def natural_sort_tuple_key(value: str):
    """Key to tuples in natural order."""
    return [natural_sort_key(v) for v in value.split("/")]


def natural_sort_key(value: str):
    """Key to strings in natural order."""
    if value.isdigit():
        return int(value)
    return value

if __name__ == "__main__":
    gdal_aero_zarr()
