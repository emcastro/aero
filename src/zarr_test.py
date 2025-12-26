from utyping import Tuple
import gc
import time

import ulogging
from geojson import GeoJsonWriter
from geolib import SideSegment, calc_bbox, convexpoly_left_right, wgs84_project
from microzarr import Zarr

ulogging.basicConfig(level=ulogging.INFO, format="%(chrono)s:%(levelname)-7s:%(name)-10s:%(message)s")
# ulogging.basicConfig(level=ulogging.DEBUG, format="%(levelname)-7s:%(name)s:%(message)s")
# ulogging.getLogger("Axis").setLevel(ulogging.DEBUG)


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
    step_m = 100
    duration = step_m / speed_mps
    warning_time_s = 30
    aircraft_time = time.time()
    aircraft_time_delta = 0.0  # 32bit float only

    for i in range(0, 150):
        azimuth = 135 - i
        aircraft = wgs84_project(aircraft, azimuth, 100)

        distance_m = speed_mps * warning_time_s

        def make_front_poly(aircraft: Tuple[float, float], azimuth: float, size_m: float):
            # Calcule le pseudo-cone devant l'avion
            #
            #         __--T--__
            #       L1        R1 (30° left and right from aircraft)
            #        \        /
            #         \      /
            #          \    /
            #          L2 | R2  (10% left and right)
            #          aircraft

            # pylint: disable=invalid-name
            T = wgs84_project(aircraft, azimuth, size_m)
            L1 = wgs84_project(aircraft, azimuth - 30, size_m)
            R1 = wgs84_project(aircraft, azimuth + 30, size_m)
            L2 = wgs84_project(aircraft, azimuth - 90, size_m * 0.10)
            R2 = wgs84_project(aircraft, azimuth + 90, size_m * 0.10)
            # pylint: enable=invalid-name

            polygon_coords = [T, R1, R2, L2, L1, T]
            return polygon_coords

        polygon_coords = make_front_poly(aircraft, azimuth, distance_m)
        left_side, right_side = convexpoly_left_right(polygon_coords)    
        lefts = [zarr.loc_at(*pt) for pt in left_side]
        rights = [zarr.loc_at(*pt) for pt in right_side]
        first_row = lefts[0][0]
        last_row = lefts[-1][0]

        left = SideSegment(lefts)
        right = SideSegment(rights)
        
        print("a", polygon_coords)
        print("b", lefts, rights, i)
        print("c", first_row, last_row)

        for row in range(first_row, last_row+1):
            start_col = round(left.x_at_y(row))
            end_col = round(right.x_at_y(row))
            
            print(row, start_col, end_col)

                

        polygon_bbox = calc_bbox(polygon_coords)
        altitude = zarr.value_at(*aircraft)
        # print(zarr.x_axis.to_idx(aircraft[0]), zarr.y_axis.to_idx(aircraft[1]), altitude, i)

        yield (
            (aircraft, altitude, azimuth, polygon_coords, polygon_bbox, aircraft_time, aircraft_time_delta, duration, i)
        )

        aircraft_time_delta += duration
    t1 = time.ticks_ms()
    print("Init      time:", time.ticks_diff(t0, tm1))
    print("Execution time:", time.ticks_diff(t1, t0))
    print("FREE1", gc.mem_free())


def write_json(result):
    with GeoJsonWriter("zones.geojson") as geojson:
        for (
            aircraft,
            elevation,
            azimuth,
            polygon_coords,
            bbox,
            aircraft_time,
            aircraft_time_delta,
            duration,
            i,
        ) in result:
            (year, month, mday, hour, minute, second, *_) = time.gmtime(aircraft_time + int(aircraft_time_delta))
            date1 = f"{year:04}-{month:02}-{mday:02}T{hour:02}:{minute:02}:{second:02}Z"
            (year, month, mday, hour, minute, second, *_) = time.gmtime(
                aircraft_time + int(aircraft_time_delta + duration)
            )
            date2 = f"{year:04}-{month:02}-{mday:02}T{hour:02}:{minute:02}:{second:02}Z"
            geojson.point(
                {"type": "point", "date1": date1, "date2": date2, "azimuth": azimuth, "elevation": elevation, "i": i},
                aircraft,
            )
            geojson.polygon(
                {"type": "zone", "date1": date1, "date2": date2, "azimuth": azimuth, "elevation": elevation, "i": i},
                polygon_coords,
            )
            geojson.bbox_polygon({"type": "bbox", "date1": date1, "date2": date2}, bbox)


def nowrite_json(result):
    for _ in result:
        pass


if __name__ == "__main__":
    write_json(run())
    # nowrite_json(run())
    gc.collect()
    print("FREE2", gc.mem_free())
