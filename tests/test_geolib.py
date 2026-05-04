# pylint: disable=import-error

import pytest
import utest  # pylint: disable=unused-import
from geodata_dump import geodump, multipoint

from geolib import (
    SideSegmentInterpolator,
    argminmax,
    calc_bbox,
    convexpoly_left_right,
    wgs84_azimuth,
    wgs84_project,
    wgs84_project_xy,
)

# epsilon used for floating point comparisons (degrees)
EPS = 1e-6
METER = 1e-5  # ~1m at the equator


def test_project_zero_distance():
    """Zero distance should return the original point."""
    point1 = (0.0, 0.0)
    point2 = (12.34, -56.78)
    result1 = wgs84_project_xy(point1[0], point1[1], 0.0, 0.0)
    result2 = wgs84_project(point2, 45.0, 0.0)
    assert result1 == point1
    assert result2 == point2
    geodump(point1)
    geodump(point2)


def test_project_consistency():
    """The tuple wrapper and xy variant must agree."""
    point = (10.0, -5.0)
    azimuth_d = 123.4
    dist_m = 10000.0
    point_result = wgs84_project(point, azimuth_d, dist_m)
    xy_result = wgs84_project_xy(point[0], point[1], azimuth_d, dist_m)
    assert point_result == xy_result
    geodump(point)
    geodump(point_result)
    geodump(xy_result)


def test_azimuth_project_consistency():
    """Project a point and verify azimuth consistency."""
    origins = [(0.0, 0.0), (45.0, 45.0), (-120.0, 30.0)]
    azimuths_d = [0.0, 90.0, 225.5, 359.9]
    dist_m = 1_000_000  # 1000 km

    for pt_idx, point in enumerate(origins):
        geodump(point, pt_idx)
        for azimuth_d in azimuths_d:
            dest = wgs84_project(point, azimuth_d, dist_m)
            calc_azimuth_d = wgs84_azimuth(point, dest)
            # forward azimuth should equal requested azimuth modulo tolerance
            assert calc_azimuth_d == pytest.approx(azimuth_d, abs=EPS)
            geodump(dest, pt_idx, azimuth_d, dist_m=dist_m)


def test_azimuth_roundtrip():
    """Project a point and verify azimuth consistency both ways at local scale."""
    origins = [(0.0, 0.0), (45.0, 45.0), (-120.0, 30.0)]
    azimuths_d = [0.0, 90.0, 225.5, 359.9]
    dist_m = 10000  # 10 km

    for pt_idx, point in enumerate(origins):
        geodump(point, pt_idx)
        for azimuth_d in azimuths_d:
            dest = wgs84_project(point, azimuth_d, dist_m)
            calc_azimuth_d = wgs84_azimuth(point, dest)
            # forward azimuth should equal requested azimuth modulo tolerance
            assert calc_azimuth_d == pytest.approx(azimuth_d, abs=EPS)
            back_azimuth_d = wgs84_azimuth(dest, point)
            expected_azimuth_d = (azimuth_d + 180.0) % 360.0
            assert back_azimuth_d == pytest.approx(expected_azimuth_d, abs=0.1)
            geodump(
                dest,
                pt_idx,
                azimuth_d,
                back_azimuth_d=back_azimuth_d,
                expected_azimuth_d=expected_azimuth_d,
            )


def test_calc_bbox_simple():
    points = [(0.0, 0.0), (10.0, -5.0), (-3.0, 4.0), (10.0, 4.0)]
    geodump(multipoint(points))
    assert geodump(calc_bbox(points)) == (-3.0, -5.0, 10.0, 4.0)
    assert geodump(calc_bbox([(1.0, 1.0)])) == (1.0, 1.0, 1.0, 1.0)


def test_argminmax():
    vals = [5.0, 1.0, 3.0, 9.0, -2.0]
    idx_min, idx_max = argminmax(vals)
    # minimum value -2.0 at index 4, maximum value 9.0 at index 3
    assert idx_min == 3
    assert idx_max == 4


def test_argminmax_all_equal():
    vals = [2.0, 2.0, 2.0]
    idx_min, idx_max = argminmax(vals)
    # all values are equal, so min and max indices should be the same (first index)
    assert idx_min == 0
    assert idx_max == 0


def test_argminmax_empty():
    vals = []
    idx_min, idx_max = argminmax(vals)
    # for an empty list, both indices should be -1
    assert idx_min == -1
    assert idx_max == -1


## TODO round robin test, clockwise and anti-clockwise


def test_convexpoly_left_right_rotations():
    """Test convexpoly_left_right with all possible rotations of the polygon."""
    # Original polygon data without the trailing first point
    unclosed_polygon = [
        (0.0, 3.0),
        (-2.0, 6.0),
        (8.0, 15.0),
        # (9.0, 15.0),
        (12.0, 10.0),
        (12.0, 9.0),
        # (6.0, 3.0),
    ]

    # Expected results for the original polygon
    expected_left = [(0.0, 3.0), (-2.0, 6.0), (8.0, 15.0)]
    expected_right = [
        (0.0, 3.0),
        #   (6.0, 3.0),
        (12.0, 9.0),
        (12.0, 10.0),
        #   (9.0, 15.0),
        (8.0, 15.0),
    ]

    # Test all rotations of the polygon
    for rotation in range(len(unclosed_polygon)):
        # Rotate the polygon by removing the first element and appending it at the end
        rotated_polygon = unclosed_polygon[rotation:] + unclosed_polygon[:rotation]
        rotated_polygon.append(rotated_polygon[0])

        # Action
        left, right = convexpoly_left_right(rotated_polygon)

        # # Assertion
        assert left == expected_left
        assert right == expected_right

        # Visualization
        geodump(rotated_polygon, rotation)
        geodump(left, rotation)
        geodump(right, rotation)


def test_sidesemgentinterpolator_x_at_y() -> None:
    # polygon anti-clockwise starting at bottom
    polygon = [(0.0, 3.0), (6.0, 3.0), (12.0, 9.0), (12.0, 10.0), (9.0, 15.0), (8.0, 15.0), (-2.0, 6.0), (0.0, 3.0)]
    polygon.reverse()

    # polygon = [(0.0, 3.0), (6.0, 3.0), (12.0, 9.0), (12.0, 10.0), (9.0, 15.0),(8.0, 15.0), (-2.0, 6.0), (0.0, 3.0)]
    left, right = convexpoly_left_right(polygon)

    assert left == [(0.0, 3.0), (-2.0, 6.0), (8.0, 15.0)]
    assert right == [(0.0, 3.0), (6.0, 3.0), (12.0, 9.0), (12.0, 10.0), (9.0, 15.0), (8.0, 15.0)]

    geodump(polygon)
    geodump(left)
    geodump(right)

    right_side = SideSegmentInterpolator(right)

    right_test_points = [(6.0, 3.0), (7.0, 4.0), (12.0, 9.0), (12.0, 9.5), (12.0, 10.0), (11.4, 11.0), (9.0, 15.0)]
    for awaited_x, y in right_test_points:
        x = right_side.x_at_y(y)
        pt = (x, y)
        right_awaited_pt = (awaited_x, y)
        # geodump(pt, "right", x, y)
        geodump(right_awaited_pt, awaited_x, y)

    left_side = SideSegmentInterpolator(right)

    left_test_points = [(0.0, 3.0), (-1.0, 4.5), (-2.0, 6.0), (0.25, 8.0), (8.0, 15.0)]
    for awaited_x, y in left_test_points:
        x = left_side.x_at_y(y)
        pt = (x, y)
        left_awaited_pt = (awaited_x, y)
        # geodump(pt, "right", x, y)
        geodump(left_awaited_pt, awaited_x, y)
