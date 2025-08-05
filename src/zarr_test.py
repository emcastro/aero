import gc
import time

import ulogging
from geolib import wgs84_project
from microzarr import Zarr

ulogging.basicConfig(level=ulogging.INFO, format="%(chrono)s:%(levelname)-7s:%(name)-10s:%(message)s")
# ulogging.basicConfig(level=ulogging.DEBUG, format="%(levelname)-7s:%(name)s:%(message)s")
ulogging.getLogger("LRUCache").setLevel(ulogging.NOLOG)


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
        azimuth = 135 - i
        x, y = wgs84_project(x, y, azimuth, 100)

        # Calcule le pseudo-cone devant l'avion

        result.append((x, y, zarr.value_at(x, y), azimuth))
    t1 = time.ticks_ms()

    with GeoJsonWrite("zones.geojson") as geojson:
        for x, y, elevation, azimuth in result:
            geojson.point(
                {"azimuth": azimuth, "elevation": elevation},
                [x, y],
            )

    print("Init      time:", time.ticks_diff(t0, tm1))
    print("Execution time:", exec_time := time.ticks_diff(t1, t0))
    print("FREE1", gc.mem_free())
    gc.collect()
    print("FREE2", gc.mem_free())
    return exec_time


if __name__ == "__main__":
    run()
