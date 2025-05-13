import struct
import array

from macropython import *

zip_path = "devdata/FRnw.zarr.zip"
index_path = "devdata/offset_table.bin"


class MemoryReader:
    def __init__(self, data: memoryview, offset: int = 0):
        self.data = data
        self.index = offset

    def consume(self, format: str):
        size = struct.calcsize(format)
        i = self.index
        result = struct.unpack(format, self.data[i : i + size])[0]
        self.index += size
        return result


class OffsetTable:
    def __init__(self, index_path: str):
        with open(index_path, "rb") as f:
            self.data = memoryview(f.read())
        self.row_index = array.array("H")

        reader = MemoryReader(self.data)

        row_count = reader.consume("<H")  # Field 0
        for row_idx in range(row_count):
            self.row_index.append(reader.index)
            self._read_row(reader, store=False)

        assert reader.index == len(self.data)

    def _read_row(self, reader: MemoryReader, store: bool):
        row_count = reader.consume("<H")  # Field 1.0

        result = [] if store else None
        for _ in range(row_count):
            tile_y = reader.consume("<H")  # Field 1.1.0
            rowpart_offset = reader.consume("<Q")  # Field 1.1.1
            rowpart_delta_count = reader.consume("<H")  # Field 1.1.2

            row_parts = [] if store else None
            for _ in range(rowpart_delta_count):
                repeated_offset_value = reader.consume("<I")  # Field 1.1.3.0
                repeated_offset_count = reader.consume("<H")  # Field 1.1.3.1
                if store:
                    row_parts.append(
                        {
                            "value": repeated_offset_value,
                            "count": repeated_offset_count,
                        }
                    )
            if store:
                result.append(
                    {
                        "tile_y": tile_y,
                        "rowpart_offset": rowpart_offset,
                        "row_parts": row_parts,
                    }
                )
        return result

    def read_row(self, row_idx: int):
        reader = MemoryReader(self.data, self.row_index[row_idx])
        return self._read_row(reader, store=True)


table = OffsetTable(index_path)

print("All data consumed")
print("Row index:", table.row_index)

row_parts = table.read_row(76)
import json
print(row_parts)

with open(zip_path, "rb") as f:
    f.seek(row_parts[0]["rowpart_offset"])
    data = f.read(row_parts[0]["row_parts"][0]["value"])
print(data[:100])

# Zip
structFileHeader = "<4s2B4HL2L2H"
sizeFileHeader = struct.calcsize(structFileHeader)
header = struct.unpack(structFileHeader, data[:sizeFileHeader])


_FH_SIGNATURE = const(0)
_FH_EXTRACT_VERSION = const(1)
_FH_EXTRACT_SYSTEM = const(2)
_FH_GENERAL_PURPOSE_FLAG_BITS = const(3)
_FH_COMPRESSION_METHOD = const(4)
_FH_LAST_MOD_TIME = const(5)
_FH_LAST_MOD_DATE = const(6)
_FH_CRC = const(7)
_FH_COMPRESSED_SIZE = const(8)
_FH_UNCOMPRESSED_SIZE = const(9)
_FH_FILENAME_LENGTH = const(10)
_FH_EXTRA_FIELD_LENGTH = const(11)

filename = data[sizeFileHeader:sizeFileHeader + header[_FH_FILENAME_LENGTH]]
# TODO check if filename is correct
zarr_data = data[sizeFileHeader + header[_FH_FILENAME_LENGTH]:]
print("+++++++++++")
# print(zarr_data)
print(len(zarr_data))
print("===============")
del zarr_data
del data
import gc
gc.collect()
print(gc.mem_free())