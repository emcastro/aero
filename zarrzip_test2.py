import struct
import array

path = 'devdata/FRnw.zarr.zip'
index_path = 'devdata/offset_table.bin'

with open(index_path, 'rb') as f:
    data = memoryview(f.read())

i = 0
def consume(format: str):
    global i
    size = struct.calcsize(format)
    result = struct.unpack(format, data[i:i+size])[0]
    i += size
    return result    

row_count = consume("<H")
row_index = array.array("H")
for row_idx in range(row_count):
    row_index.append(i)
    row_count = consume("<H")
    for _ in range(row_count):
        tile_y = consume("<H")
        rowpart_offset = consume("<Q")
        rowpart_delta_count = consume("<H")
        print("Row part", row_idx, tile_y, rowpart_offset, rowpart_delta_count)
        for _ in range(rowpart_delta_count):
            repeated_offset_value = consume("<I")
            repeated_offset_count = consume("<H")

assert i == len(data)

print("All data consumed")
print("Row index:", row_index)	