# pylint: disable=import-error

import pytest
import utest  # pylint: disable=unused-import
from geodata_dump import geodump, multipoint

from geolib import (
    SideSegmentInterpolator,
    calc_bbox,
    convexpoly_left_right,
    find_idx_left_bottom_and_top,
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
    origins = [(0.0, 0.0), (45.0, 45.0), (10.0, -20.0), (30.0, -40.0), (50.0, -10.0)]
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


def test_azimuth_negative():
    """Negative azimuths produce same dest as their positive equivalent."""
    neg_azimuths_d = [-25.0, -45.0, -90.0, -160.0]
    pos_azimuths_d = [x + 360.0 for x in neg_azimuths_d]
    origins = [(-60.0, -20.0), (-55.0, -15.0), (-65.0, -25.0)]
    dist_m = 10000

    for pt_idx, point in enumerate(origins):
        geodump(point, pt_idx)
        for neg_az, pos_az in zip(neg_azimuths_d, pos_azimuths_d):
            dest_neg = wgs84_project(point, neg_az, dist_m)
            dest_pos = wgs84_project(point, pos_az, dist_m)
            assert dest_neg == pytest.approx(dest_pos, abs=METER)


def test_azimuth_roundtrip():
    """Project a point and verify azimuth consistency both ways at local scale."""
    origins = [(10.0, -20.0), (30.0, -40.0), (50.0, -10.0)]
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


def test_find_idx_left_bottom_and_top():
    points = [(-60.0, 0.0), (-55.0, -1.0), (-65.0, 5.0), (-67.0, 10.0),(-70.0, 10.0), (-65.0, -2.0), (-64.0, -2.0), (-60.0, 1.0)]
    geodump(points)
    idx_left_bottom, idx_left_top = find_idx_left_bottom_and_top(points)
    assert idx_left_bottom == 5
    assert idx_left_top == 4
    geodump(points[idx_left_bottom], idx_left_bottom)
    geodump(points[idx_left_top], idx_left_top)


def test_convexpoly_left_right_rotations():
    """Test convexpoly_left_right with all possible rotations of the polygon."""
    # Original polygon data without the trailing first point
    unclosed_polygon = [
        (-65.0, -2.0),
        (-67.0, 1.0),
        (-57.0, 10.0),
        (-56.0, 10.0),
        (-53.0, 5.0),
        (-53.0, 4.0),
        (-59.0, -2.0),
    ]

    geodump(unclosed_polygon)

    # Expected results for the original polygon
    expected_left = [(-65.0, -2.0), (-67.0, 1.0), (-57.0, 10.0)]
    expected_right = [
        (-65.0, -2.0),
        (-59.0, -2.0),
        (-53.0, 4.0),
        (-53.0, 5.0),
        (-56.0, 10.0),
        (-57.0, 10.0),
    ]

    geodump(expected_left)
    geodump(expected_right)

    # Test all rotations of the polygon
    for reverse in [False, True]:
        for rotation in range(len(unclosed_polygon)):
            # Rotate the polygon by removing the first element and appending it at the end
            rotated_polygon = unclosed_polygon[rotation:] + unclosed_polygon[:rotation]
            rotated_polygon.append(rotated_polygon[0])
            if reverse:
                rotated_polygon.reverse()

            # Action
            left, right = convexpoly_left_right(rotated_polygon)

            # Assertion (only for original orientation; expected values are hardcoded for it)
            assert left == expected_left
            assert right == expected_right

            # Visualization
            geodump(rotated_polygon, rotation)
            geodump(left, rotation)
            geodump(right, rotation)


def test_sidesegmentinterpolator_x_at_y():
    # polygon anti-clockwise starting at bottom
    polygon = [
        (-59.0, -2.0),
        (-53.0, 4.0),
        (-53.0, 5.0),
        (-56.0, 10.0),
        (-57.0, 10.0),
        (-67.0, 1.0),
        (-65.0, -2.0),
        (-59.0, -2.0),
    ]

    polygon.reverse()
    left, right = convexpoly_left_right(polygon)

    assert left == [(-65.0, -2.0), (-67.0, 1.0), (-57.0, 10.0)]
    assert right == [(-65.0, -2.0), (-59.0, -2.0), (-53.0, 4.0), (-53.0, 5.0), (-56.0, 10.0), (-57.0, 10.0)]

    geodump(polygon)
    geodump(left)
    geodump(right)

    right_side = SideSegmentInterpolator(right)

    right_test_points = [
        (-59.0, -2.0),
        (-58.0, -1.0),
        (-53.0, 4.0),
        (-53.0, 4.5),
        (-53.0, 5.0),
        (-53.6, 6.0),
        (-56.0, 10.0),
    ]
    for awaited_x, y in right_test_points:
        x = right_side.x_at_y(y)
        right_awaited_pt = (awaited_x, y)
        right_pt=(x,y)
        geodump(right_awaited_pt, awaited_x, y)
        geodump(right_pt, x, y)
        assert x == pytest.approx(awaited_x, abs=EPS)

    left_side = SideSegmentInterpolator(left)

    left_test_points = [(-65.0, -2.0), (-66.0, -0.5), (-67.0, 1.0), (-64.0, 3.7), (-57.0, 10.0)]
    for awaited_x, y in left_test_points:
        x = left_side.x_at_y(y)
        left_awaited_pt = (awaited_x, y)
        left_pt=(x,y)
        geodump(left_awaited_pt, awaited_x, y)
        geodump(left_pt, x, y)
        assert x == pytest.approx(awaited_x, abs=EPS)


def test_convexpoly_left_right_empty():
    left, right = convexpoly_left_right([])
    assert left == []
    assert right == []
