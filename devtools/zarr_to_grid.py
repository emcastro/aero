import click
import fiona
import rasterio
from rasterio.windows import Window, bounds


def get_tile_features_rasterio(zarr_path):
    with rasterio.open(zarr_path) as src:
        block_shapes = src.block_shapes
        assert block_shapes
        block_height, block_width = block_shapes[0]
        width, height = src.width, src.height
        n_tiles_x = (width + block_width - 1) // block_width
        n_tiles_y = (height + block_height - 1) // block_height
        for chunk_row in range(n_tiles_y):
            for chunk_column in range(n_tiles_x):
                col_offset = chunk_column * block_width
                row_offset = chunk_row * block_height
                w = min(block_width, width - col_offset)
                h = min(block_height, height - row_offset)
                win = Window(col_offset, row_offset, w, h)  # type: ignore
                bbox = bounds(win, src.transform)
                # Polygon as list of coordinates (GeoJSON format)
                poly = {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [bbox[0], bbox[1]],
                            [bbox[2], bbox[1]],
                            [bbox[2], bbox[3]],
                            [bbox[0], bbox[3]],
                            [bbox[0], bbox[1]],
                        ]
                    ],
                }
                yield {
                    "type": "Feature",
                    "geometry": poly,
                    "properties": {"chunk_column": chunk_column, "chunk_row": chunk_row},
                }


@click.command()
@click.option("--out", "-o", help="Output name for the GeoJson grid file.")
@click.argument("source")
def zarr_to_fgb_tiles(out, source):
    fc = get_tile_features_rasterio(source)

    schema = {
        "geometry": "Polygon",
        "properties": {"chunk_column": "int", "chunk_row": "int"},
    }

    with fiona.open(
        out,
        "w",
        driver="FlatGeobuf",
        crs="EPSG:4326",
        schema=schema,
    ) as fgb:
        fgb.writerecords(fc)
    print("Done")


if __name__ == "__main__":
    zarr_to_fgb_tiles()  # pylint: disable=no-value-for-parameter
