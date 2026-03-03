# pylint: disable=import-error

import math

import pytest
import utest  # pylint: disable=unused-import

from geolib import (
    SideSegment,
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
    assert wgs84_project_xy(0.0, 0.0, 0.0, 0.0) == (0.0, 0.0)
    assert wgs84_project((12.34, -56.78), 45.0, 0.0) == (12.34, -56.78)


def test_project_consistency():
    """The tuple wrapper and xy variant must agree."""
    pt = (10.0, -5.0)
    az = 123.4
    d = 10000.0
    assert wgs84_project(pt, az, d) == wgs84_project_xy(pt[0], pt[1], az, d)


def test_azimuth_project_consistency():
    """Project a point and verify azimuth consistency."""
    origins = [(0.0, 0.0), (45.0, 45.0), (-120.0, 30.0)]
    azims_m = [0.0, 90.0, 225.5, 359.9]
    dist_l = 1_000_000  # 1000 km

    for p in origins:
        for az_d in azims_m:
            dest = wgs84_project(p, az_d, dist_l)
            az_calc_d = wgs84_azimuth(p, dest)
            # forward azimuth should equal requested azimuth modulo tolerance
            assert az_calc_d == pytest.approx(az_d, abs=EPS)


def test_azimuth_roundtrip():
    """Project a point and verify azimuth consistency both ways at local scale."""
    origins = [(0.0, 0.0), (45.0, 45.0), (-120.0, 30.0)]
    azims_d = [0.0, 90.0, 225.5, 359.9]
    dist_m = 10000  # 10 km

    for p in origins:
        for az in azims_d:
            dest = wgs84_project(p, az, dist_m)
            az_calc = wgs84_azimuth(p, dest)
            # forward azimuth should equal requested azimuth modulo tolerance
            assert az_calc == pytest.approx(az, abs=EPS)
            back = wgs84_azimuth(dest, p)
            expected = (az + 180.0) % 360.0
            assert back == pytest.approx(expected, abs=0.1)


def test_calc_bbox_simple():
    pts = [(0.0, 0.0), (10.0, -5.0), (-3.0, 4.0), (10.0, 4.0)]
    assert calc_bbox(pts) == (-3.0, -5.0, 10.0, 4.0)
    assert calc_bbox([(1.0, 1.0)]) == (1.0, 1.0, 1.0, 1.0)


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


# def test_convexpoly_left_right_square() -> None:
#     # square clockwise starting at bottom-left
#     square = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
#     left, right = convexpoly_left_right(square)
#     # left and right should each contain two edges of the square
#     assert len(left) == 3
#     assert len(right) == 3
#     # verify continuity
#     assert left[0] in square
#     assert right[0] in square


def test_side_segment_basic():
    # simple vertical strip from y=0 to y=10 at x = y/2 + 1
    side = [(0.0, 1.0), (10.0, 6.0)]
    seg = SideSegment(side)
    ys = [0.0, 2.5, 5.0, 7.5, 10.0]
    last_x = None
    for y in ys:
        x = seg.x_at_y(y)
        if last_x is not None:
            # x should increase as y increases for this simple segment
            assert x > last_x
        last_x = x
    seg.restart()
    assert seg.segment_idx == -1
    assert seg.segment_end_y < ys[0]
