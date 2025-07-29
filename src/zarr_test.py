import time
from microzarr import Zarr
from geolib import wgs84_project
import gc

import ulogging

# ulogging.basicConfig(level=ulogging.DEBUG, format="%(levelname)-7s:%(name)s:%(message)s")
ulogging.basicConfig(level=ulogging.CRITICAL, format="%(chrono)s:%(levelname)-7s:%(name)s:%(message)s")


def run():
    """
    This script demonstrates the usage of the Zarr library and the `wgs84_project` function.
    It projects a point along a great circle path and retrieves elevation data from a Zarr dataset.
    """
    tm1 = time.ticks_ms()

    zarr = Zarr("/sd/dem.zarr")
    gc.collect()  # Clean up temp object from Zarr reading

    t0 = time.ticks_ms()
    x = -0.4561
    y = 49.17617
    result = []
    for i in range(0, 100):
        x, y = wgs84_project(x, y, 135, 100)
        result.append((x, y, zarr.value_at(x, y)))
    t1 = time.ticks_ms()
    for line in result:
        print(*line)
    print("Init      time:", time.ticks_diff(t0, tm1))
    print("Execution time:", exec_time := time.ticks_diff(t1, t0))
    print("FREE1", gc.mem_free())
    gc.collect()
    print("FREE2", gc.mem_free())
    return exec_time


if __name__ == "__main__":
    run()
