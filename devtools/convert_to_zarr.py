import struct
import json
import os
import re
import zipfile

import click
import rasterio
from rasterio.merge import merge
from typing import List

BLOCKSIZE = 100


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
    offset_table = OffsetTable()
    previous_x = -1
    previous_y = None

    tile_index_re = re.compile(r".*/(\d+)/(\d+)")

    zip_filename = f"{out}.zip"

    files = [os.path.join(root, file) for root, _, files in os.walk(out) for file in files]

    with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_STORED) as zipf:
        for file_path in sorted(files, key=natural_sort_tuple_key):
            print("Adding file:", file_path)
            arcname = os.path.relpath(file_path, start=os.path.dirname(out))
            zipf.write(file_path, arcname=arcname)
            info = zipf.getinfo(arcname)

            offset = info.header_offset

            match = tile_index_re.match(arcname)
            if match:
                tile_x_str, tile_y_str = match.groups()
                tile_x, tile_y = int(tile_x_str), int(tile_y_str)

                new_row = previous_x != tile_x
                if new_row:
                    # if rows a missing (no_data), add them
                    for padding_tile_x in range(previous_x + 1, tile_x):
                        offset_table.new_row(padding_tile_x)
                    offset_table.new_row(tile_x)

                new_column = previous_y != tile_y - 1
                if new_column:
                    offset_table.absolute_column(tile_y, offset)

                if not new_column:
                    assert not new_row
                    size = offset - previous_offset
                    offset_table.relative_offset(size)

                previous_y = tile_y
                previous_x = tile_x

            previous_offset = offset

    print(f"Zarr file has been zipped as {zip_filename}")
    offset_table.dump()


def natural_sort_tuple_key(value: str):
    """Key to tuples in natural order."""
    return [natural_sort_key(v) for v in value.split("/")]


def natural_sort_key(value: str):
    """Key to strings in natural order."""
    if value.isdigit():
        return int(value)
    return value


from dataclasses import dataclass, asdict


@dataclass
class RepeatedOffset:
    value: int
    count: int


@dataclass
class RowPart:
    offset: int
    deltas: List[RepeatedOffset]


class OffsetTable:
    def __init__(self):
        self.rows = []
        self.current_row = None
        self.current_row_part = None

    def new_row(self, tile_x):
        print("New row", tile_x)
        assert tile_x == len(self.rows)
        self.current_row = {}
        self.rows.append(self.current_row)

    def absolute_column(self, tile_y, offset):
        assert tile_y not in self.current_row
        self.current_row_part = RowPart(offset, [])
        self.current_row[tile_y] = self.current_row_part

    def relative_offset(self, size):
        # Get the last offset in the current row part
        if self.current_row_part.deltas == []:
            self.current_row_part.deltas.append(RepeatedOffset(size, 1))
        elif self.current_row_part.deltas[-1].value != size:
            self.current_row_part.deltas.append(RepeatedOffset(size, 1))
        else:
            current_repeated_offset = self.current_row_part.deltas[-1]
            if current_repeated_offset.value == size:
                current_repeated_offset.count += 1

    def dump(self):

        # Write the offset table to a binary file
        with open("offset_table.bin", "bw") as f:
            f.write(struct.pack("<H", len(self.rows)))  # Field 0
            for row in self.rows:
                f.write(struct.pack("<H", len(row)))  # Field 1.0
                for tile_y, row_part in row.items():
                    f.write(struct.pack("<H", tile_y))  # Field 1.1.0
                    f.write(struct.pack("<Q", row_part.offset))  # Field 1.1.1
                    f.write(struct.pack("<H", len(row_part.deltas)))  # Field 1.1.2
                    for repeated_offset in row_part.deltas:
                        f.write(struct.pack("<I", repeated_offset.value))  # Field 1.1.3.0
                        f.write(struct.pack("<H", repeated_offset.count))  # Field 1.1.3.1

        # Write the offset table to a JSON file (for debugging)
        with open("offset_table.json", "w") as f:
            json.dump(self.rows, f, indent=2, cls=DataclassEncoder)


class DataclassEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "__dataclass_fields__"):
            return obj.__dict__
        return super().default(obj)


if __name__ == "__main__":
    gdal_aero_zarr()
