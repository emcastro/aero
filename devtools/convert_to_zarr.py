import os
import re
import zipfile

import click
import rasterio
from rasterio.merge import merge

BLOCKSIZE = 30


@click.command()
@click.option("--out", "-o", help="Output name for the Zarr file.")
@click.argument("sources", nargs=-1)  # Accept multiple tile names as arguments.
def gdal_aero_zarr(out, sources):
    print(sources, out)

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

    # Create a ZIP file from the Zarr output
    offset = 0

    zip_filename = f"{out}.zip"
    with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_STORED) as zipf:
        for root, _, files in sorted(os.walk(out)):
            for file in sorted(files, key=natural_sort_key):
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, start=os.path.dirname(out))
                zipf.write(file_path, arcname=arcname)
                print(arcname)
                info = zipf.getinfo(arcname)
                print(info, info.header_offset, info.header_offset- offset)
                offset = info.header_offset

    print(f"Zarr file has been zipped as {zip_filename}")


def natural_sort_key(value: str):
    """Key to strings in natural order."""
    if value.isdigit():
        return int(value)
    return value


if __name__ == "__main__":
    gdal_aero_zarr()
