import time
from microzarr import Zarr
from geolib import wgs84_project


def run():
    """
    This script demonstrates the usage of the Zarr library and the `wgs84_project` function.
    It projects a point along a great circle path and retrieves elevation data from a Zarr dataset.
    """
    tm1 = time.time_ns()
    zarr = Zarr("devdata/FRnw.zarr")

    t0 = time.time_ns()
    x = -0.4561
    y = 49.17617
    result = []
    for i in range(0,100):
        x, y = wgs84_project(x, y, 135, 100)
        result.append((x, y, zarr.value_at(x, y)))
    t1 = time.time_ns()
    for line in result:
        print(*line)
    print("Init       time:", (t0 - tm1)/1e9)
    print("Execution time:", (t1 - t0)/1e9)

run()
