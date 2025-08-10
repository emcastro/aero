import gc
import time

import ulogging
from geojson import GeoJsonWriter
from geolib import calc_bbox, wgs84_project
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
    aircraft = (x, y)
    speed_mps = 60.0
    warning_time_s = 30
    aircraft_time = time.time()
    aircraft_time_delta = 0.0  # 32bit float only
    result = []
    for i in range(0, 62):
        azimuth = 135 - i
        aircraft = wgs84_project(aircraft, azimuth, 100)

        # Calcule le pseudo-cone devant l'avion
        #
        #         __--T--__
        #       L1        R1 (30° left and right from aircraft)
        #        \        /
        #         \      /
        #          \    /
        #          L2 | R2  (10% left and right)
        #          aircraft
        distance_m = speed_mps * warning_time_s

        # pylint: disable=invalid-name
        T = wgs84_project(aircraft, azimuth, distance_m)
        L1 = wgs84_project(aircraft, azimuth - 30, distance_m)
        R1 = wgs84_project(aircraft, azimuth + 30, distance_m)
        L2 = wgs84_project(aircraft, azimuth - 90, distance_m * 0.10)
        R2 = wgs84_project(aircraft, azimuth + 90, distance_m * 0.10)
        # pylint: enable=invalid-name

        polygon_coords = [T, R1, R2, aircraft, L2, L1, T]

        polygon_bbox = calc_bbox(polygon_coords)

        result.append(
            (
                aircraft,
                zarr.value_at(*aircraft),
                azimuth,
                polygon_coords,
                polygon_bbox,
                aircraft_time,
                aircraft_time_delta,
            )
        )

        aircraft_time_delta += 100 / speed_mps
    t1 = time.ticks_ms()

    with GeoJsonWriter("zones.geojson") as geojson:
        for aircraft, elevation, azimuth, polygon_coords, bbox, aircraft_time, aircraft_time_delta in result:
            (year, month, mday, hour, minute, second, *_) = time.gmtime(aircraft_time + int(aircraft_time_delta))
            date = f"{year:04}-{month:02}-{mday:02}T{hour:02}:{minute:02}:{second+aircraft_time_delta%1:02}Z"
            geojson.point(
                {"date": date, "azimuth": azimuth, "elevation": elevation},
                aircraft,
            )
            geojson.polygon(
                {"timestamp": aircraft_time_delta ,"date": date, "azimuth": azimuth, "elevation": elevation},
                polygon_coords,
            )
            geojson.bbox_polygon({"date": date}, bbox)

    del result
    print("Init      time:", time.ticks_diff(t0, tm1))
    print("Execution time:", exec_time := time.ticks_diff(t1, t0))
    print("FREE1", gc.mem_free())
    gc.collect()
    print("FREE2", gc.mem_free())
    return exec_time


if __name__ == "__main__":
    run()
