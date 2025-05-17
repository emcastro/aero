import time
from microzarr import Zarr
from geolib import wgs84_project
import gc

def run():
    """
    This script demonstrates the usage of the Zarr library and the `wgs84_project` function.
    It projects a point along a great circle path and retrieves elevation data from a Zarr dataset.
    """
    tm1 = time.time()
    zarr = Zarr("devdata/FRnw.zarr")
    gc.collect() # Clean up temp object from Zarr reading

    t0 = time.time()
    x = -0.4561
    y = 49.17617
    result = []
    for i in range(0,100):
        x, y = wgs84_project(x, y, 135, 100)
        result.append((x, y, zarr.value_at(x, y)))
    t1 = time.time()
    for line in result:
        print(*line)
    print("Init      time:", t0 - tm1)
    print("Execution time:", t1 - t0)

run()
