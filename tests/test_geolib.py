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

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def epsilon_coord():
    """Tolerance for coordinate comparisons."""
    return 1e-6


# ============================================================================
# Test WGS84 Projection
# ============================================================================


class TestWgs84ProjectXY:
    """Test geographic projection along great circle paths."""

    def assert_coord_equal(self, pt1, pt2, places=6):
        """Assert that two coordinates are almost equal."""
        assert abs(pt1[0] - pt2[0]) < 10 ** (-places), f"Longitude mismatch: {pt1[0]} vs {pt2[0]}"
        assert abs(pt1[1] - pt2[1]) < 10 ** (-places), f"Latitude mismatch: {pt1[1]} vs {pt2[1]}"

    def test_zero_distance_returns_same_point(self):
        """Test that zero distance returns the same point."""
        lon, lat = -0.5, 48.5
        result = wgs84_project_xy(lon, lat, azimuth=0, distance=0)
        self.assert_coord_equal(result, (lon, lat))

    @pytest.mark.parametrize(
        "azimuth,expected_lon_delta,expected_lat_delta",
        [
            (0, 0, 1),  # North
            (180, 0, -1),  # South
            (90, 1, 0),  # East
            (270, -1, 0),  # West
        ],
    )
    def test_cardinal_projections(self, azimuth, expected_lon_delta, expected_lat_delta):
        """Test cardinal direction projections."""
        lon, lat = 0.0, 0.0
        distance_m = 111320  # ~1 degree at equator
        result = wgs84_project_xy(lon, lat, azimuth=azimuth, distance=distance_m)
        assert abs(result[0] - (lon + expected_lon_delta)) < 0.1
        assert abs(result[1] - (lat + expected_lat_delta)) < 0.1

    def test_northeast_projection(self):
        """Test NE projection (45 degrees)."""
        lon, lat = 0.0, 0.0
        distance_m = 111320 * math.sqrt(2)
        result = wgs84_project_xy(lon, lat, azimuth=45, distance=distance_m)
        assert result[0] > lon
        assert result[1] > lat

    def test_negative_azimuth_equivalent_to_positive(self):
        """Test negative azimuth equals 360 - azimuth."""
        lon, lat = 0.0, 0.0
        distance_m = 111320
        result_neg = wgs84_project_xy(lon, lat, azimuth=-90, distance=distance_m)
        result_pos = wgs84_project_xy(lon, lat, azimuth=270, distance=distance_m)
        self.assert_coord_equal(result_neg, result_pos, places=5)

    def test_negative_distance_reverses_direction(self):
        """Test negative distance reverses direction."""
        lon, lat = 0.0, 0.0
        distance_m = 111320
        result_forward = wgs84_project_xy(lon, lat, azimuth=0, distance=distance_m)
        result_backward = wgs84_project_xy(lon, lat, azimuth=180, distance=-distance_m)
        self.assert_coord_equal(result_forward, result_backward, places=5)

    @pytest.mark.parametrize("latitude", [0.0, 45.0, 80.0])
    def test_various_latitudes(self, latitude):
        """Test projection at various latitudes."""
        lon = 0.0
        distance_m = 111320 * 2
        result = wgs84_project_xy(lon, latitude, azimuth=0, distance=distance_m)
        assert result[1] > latitude, f"Should move north from {latitude}"

    def test_roundtrip_projection(self):
        """Test forward and reverse projections return to origin."""
        lon, lat = 10.0, 48.5
        azimuth = 135
        distance = 50000
        intermediate = wgs84_project_xy(lon, lat, azimuth, distance)
        reverse_azimuth = (azimuth + 180) % 360
        result = wgs84_project_xy(intermediate[0], intermediate[1], reverse_azimuth, distance)
        self.assert_coord_equal(result, (lon, lat), places=2)


class TestWgs84Project:
    """Test tuple-based geographic projection wrapper."""

    def test_tuple_variant_consistency(self):
        """Test tuple variant matches xy variant."""
        pt = (-0.5, 48.5)
        azimuth = 45
        distance = 10000
        result_tuple = wgs84_project(pt, azimuth, distance)
        result_xy = wgs84_project_xy(pt[0], pt[1], azimuth, distance)
        assert abs(result_tuple[0] - result_xy[0]) < 1e-6
        assert abs(result_tuple[1] - result_xy[1]) < 1e-6

    def test_tuple_projection(self):
        """Test basic tuple projection."""
        pt = (0.0, 0.0)
        result = wgs84_project(pt, azimuth=0, distance=111320)
        assert result[1] > pt[1]


# ============================================================================
# Test WGS84 Azimuth
# ============================================================================


class TestWgs84Azimuth:
    """Test azimuth calculations between points."""

    @pytest.mark.parametrize(
        "pt1,pt2,expected_azimuth",
        [
            ((0.0, 0.0), (0.0, 1.0), 0.0),  # North
            ((0.0, 0.0), (1.0, 0.0), 90.0),  # East
            ((0.0, 1.0), (0.0, 0.0), 180.0),  # South
            ((1.0, 0.0), (0.0, 0.0), 270.0),  # West
            ((0.0, 0.0), (1.0, 1.0), 45.0),  # Northeast
        ],
    )
    def test_cardinal_azimuths(self, pt1, pt2, expected_azimuth):
        """Test cardinal direction azimuths."""
        azimuth = wgs84_azimuth(pt1, pt2)
        assert abs(azimuth - expected_azimuth) < 1.0, f"Expected ~{expected_azimuth}°, got {azimuth}°"

    def test_reciprocal_azimuths_differ_by_180(self):
        """Test that A->B azimuth differs from B->A by 180 degrees."""
        pt1 = (0.0, 0.0)
        pt2 = (1.0, 1.0)
        az_forward = wgs84_azimuth(pt1, pt2)
        az_backward = wgs84_azimuth(pt2, pt1)
        diff = abs(az_forward - az_backward)
        if diff > 180:
            diff = 360 - diff
        assert abs(diff - 180.0) < 1.0

    def test_azimuth_always_in_range(self):
        """Test that azimuth is always in [0, 360)."""
        test_points = [
            ((0.0, 0.0), (1.0, 1.0)),
            ((10.0, 50.0), (-5.0, 60.0)),
            ((179.0, 0.0), (-179.0, 0.0)),
        ]
        for pt1, pt2 in test_points:
            azimuth = wgs84_azimuth(pt1, pt2)
            assert 0.0 <= azimuth < 360.0, f"Azimuth {azimuth} out of range [0, 360)"


# ============================================================================
# Test Bounding Box
# ============================================================================


class TestCalcBbox:
    """Test bounding box calculation."""

    @pytest.mark.parametrize(
        "coords,expected",
        [
            ([(5.0, 10.0)], (5.0, 10.0, 5.0, 10.0)),  # Single point
            ([(0.0, 0.0), (2.0, 3.0)], (0.0, 0.0, 2.0, 3.0)),  # Two points
            ([(-5.0, -10.0), (5.0, 10.0), (0.0, 0.0)], (-5.0, -10.0, 5.0, 10.0)),  # Negative coords
        ],
    )
    def test_bbox_calculation(self, coords, expected):
        """Test bbox with various coordinate sets."""
        bbox = calc_bbox(coords)
        assert bbox == expected

    def test_bbox_with_repeated_coordinates(self):
        """Test bbox with repeated coordinates."""
        coords = [(1.0, 2.0), (1.0, 2.0), (3.0, 4.0)]
        bbox = calc_bbox(coords)
        assert bbox == (1.0, 2.0, 3.0, 4.0)

    def test_bbox_grid_of_points(self):
        """Test bbox for grid of points."""
        coords = [(float(i), float(j)) for i in range(-2, 3) for j in range(-3, 4)]
        bbox = calc_bbox(coords)
        assert bbox == (-2.0, -3.0, 2.0, 3.0)

    @pytest.mark.parametrize(
        "q,coords,expected",
        [
            ("Q1", [(1.0, 1.0), (2.0, 3.0)], (1.0, 1.0)),
            ("Q2", [(-2.0, 1.0), (-1.0, 3.0)], (-2.0, 1.0)),
            ("Q3", [(-2.0, -3.0), (-1.0, -1.0)], (-2.0, -3.0)),
            ("Q4", [(1.0, -3.0), (2.0, -1.0)], (1.0, -3.0)),
        ],
    )
    def test_bbox_in_quadrants(self, q, coords, expected):
        """Test bbox in all four quadrants."""
        bbox = calc_bbox(coords)
        assert (bbox[0], bbox[1]) == expected


# ============================================================================
# Test Argminmax
# ============================================================================


class TestArgminmax:
    """Test finding indices of min and max values."""

    @pytest.mark.parametrize(
        "items,expected_min_val,expected_max_val",
        [
            ([3.0, 1.0, 4.0, 1.0, 5.0], 5.0, 1.0),  # idx_min -> max, idx_max -> min
            ([42.0], 42.0, 42.0),  # Single element
            ([5.0, 5.0, 5.0], 5.0, 5.0),  # All same
            ([-3.0, -1.0, -5.0], -1.0, -5.0),  # Negative values
        ],
    )
    def test_argminmax_calculation(self, items, expected_min_val, expected_max_val):
        """Test min/max index detection."""
        idx_min, idx_max = argminmax(items)
        assert items[idx_min] == expected_min_val
        assert items[idx_max] == expected_max_val


# ============================================================================
# Test Convex Polygon
# ============================================================================


class TestConvexPolyLeftRight:
    """Test convex polygon side splitting."""

    def test_square_polygon_splits(self):
        """Test splitting square polygon."""
        points = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
        left, right = convexpoly_left_right(points)
        assert len(left) > 0
        assert len(right) > 0
        assert len(left) + len(right) >= len(points)

    def test_pentagon_polygon_splits(self):
        """Test splitting pentagon polygon."""
        points = [(0.0, 0.0), (2.0, 0.0), (3.0, 1.5), (1.5, 3.0), (-0.5, 2.0)]
        left, right = convexpoly_left_right(points)
        assert len(left) > 0
        assert len(right) > 0


# ============================================================================
# Test SideSegment
# ============================================================================


class TestSideSegment:
    """Test SideSegment class for polygon side interpolation."""

    def test_horizontal_segment(self):
        """Test x_at_y on horizontal line segment."""
        side = [(0.0, 5.0), (5.0, 5.0), (10.0, 5.0)]
        segment = SideSegment(side)
        x = segment.x_at_y(5.0)
        assert 0.0 <= x <= 10.0

    def test_diagonal_segment(self):
        """Test x_at_y on diagonal line segment."""
        side = [(0.0, 0.0), (5.0, 5.0), (10.0, 10.0)]
        segment = SideSegment(side)
        x = segment.x_at_y(5.0)
        assert abs(x - 5.0) < 1e-5

    def test_sequential_y_queries(self):
        """Test sequential y-value queries in increasing order."""
        side = [(0.0, 0.0), (5.0, 10.0), (10.0, 20.0)]
        segment = SideSegment(side)
        x1 = segment.x_at_y(2.0)
        x2 = segment.x_at_y(5.0)
        x3 = segment.x_at_y(15.0)
        assert x1 is not None
        assert x2 is not None
        assert x3 is not None

    def test_restart_resets_state(self):
        """Test that restart() resets internal state."""
        side = [(0.0, 0.0), (10.0, 10.0)]
        segment = SideSegment(side)
        x1 = segment.x_at_y(5.0)
        segment.restart()
        x2 = segment.x_at_y(5.0)
        assert abs(x1 - x2) < 1e-5
