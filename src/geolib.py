from math import asin, atan2, cos, degrees, radians, sin

from utyping import List, Tuple

# Average radius of the Earth in meters
R = const(6371008.8)


# Projects a point from lat/lon on the great circle with azimuth alpha (in degrees)
# at a distance (in meters)
def wgs84_project_xy(lon: float, lat: float, azimuth: float, distance: float) -> Tuple[float, float]:
    """
    Projects a point from latitude/longitude along a great circle path with a given
    azimuth and distance (Vincenty formula).

    Args:
        lon (float): Longitude of the starting point.
        lat (float): Latitude of the starting point.
        azimuth (float): Azimuth angle in degrees.
        distance (float): Distance to project in meters.

    Returns:
        tuple: A tuple containing the longitude and latitude of the projected point.
    """
    # Convert initial values to radians
    lat = radians(lat)
    lon = radians(lon)
    azimuth = radians(azimuth)

    # Calculate the angular distance
    delta = distance / R

    cos_lat = cos(lat)
    sin_lat = sin(lat)
    cos_delta = cos(delta)
    sin_delta = sin(delta)

    # Calculate the latitude of target in radians
    target_lat = asin(sin_lat * cos_delta + cos_lat * sin_delta * cos(azimuth))

    # Calculate the longitude difference in radians
    delta_lon = atan2(sin(azimuth) * sin_delta * cos_lat, cos_delta - sin_lat * sin(target_lat))

    # Calculate the longitude of target in radians
    target_lon = lon + delta_lon

    # Convert the results to degrees
    target_lat = degrees(target_lat)
    target_lon = degrees(target_lon)

    return target_lon, target_lat


def wgs84_project(pt: Tuple[float, float], azimuth: float, distance: float):
    """
    Projects a point along a great circle path with a given azimuth and distance.
    Same implementation as `wgs84_project`, but takes a point tuple as input.

    Args:
        pt (tuple): A tuple containing the longitude and latitude of the starting point.
        azimuth (float): Azimuth angle in degrees.
        distance (float): Distance to project in meters.

    Returns:
        tuple: A tuple containing the longitude and latitude of the projected point.
    """
    return wgs84_project_xy(pt[0], pt[1], azimuth, distance)


def wgs84_azimuth(pt1: Tuple[float, float], pt2: Tuple[float, float]) -> float:
    """
    Calculates the azimuth from pt1 to pt2.

    Args:
        pt1 (tuple): A tuple containing the longitude and latitude of the first point.
        pt2 (tuple): A tuple containing the longitude and latitude of the second point.

    Returns:
        float: The azimuth angle in degrees from pt1 to pt2.
    """
    lon1, lat1 = radians(pt1[0]), radians(pt1[1])
    lon2, lat2 = radians(pt2[0]), radians(pt2[1])

    dlon = lon2 - lon1
    x = sin(dlon) * cos(lat2)
    y = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dlon)

    azimuth = atan2(x, y)
    return degrees(azimuth) % 360


MINUS_INF = float("-inf")
PLUS_INF = float("inf")


# pylint: disable=consider-using-min-builtin, consider-using-max-builtin
def calc_bbox(coords: List[Tuple[float, float]]):
    """
    Computes the bounding box for a list of coordinates.

    Args:
        coords (list): A list of tuples containing longitude and latitude pairs.

    Returns:
        tuple: A tuple containing the minimum longitude, minimum latitude,
               maximum longitude, and maximum latitude.
    """

    min_lon = PLUS_INF
    max_lon = MINUS_INF
    min_lat = PLUS_INF
    max_lat = MINUS_INF

    for lon, lat in coords:
        if lon < min_lon:  # pragma: no mutate
            min_lon = lon
        if lon > max_lon:  # pragma: no mutate
            max_lon = lon
        if lat < min_lat:  # pragma: no mutate
            min_lat = lat
        if lat > max_lat:  # pragma: no mutate
            max_lat = lat

    return min_lon, min_lat, max_lon, max_lat


def find_idx_left_bottom_and_top(points: List[Tuple[float, float]]):
    if not points:
        return -1, -1
    idx_left_bottom = 0
    idx_left_top = 0
    min_y = points[0][1]
    max_y = points[0][1]
    min_x_at_min_y = points[0][0]
    min_x_at_max_y = points[0][0]
    for i, (x, y) in enumerate(points):
        if y < min_y or (y == min_y and x < min_x_at_min_y):
            min_y = y
            min_x_at_min_y = x
            idx_left_bottom = i
        if y > max_y or (y == max_y and x < min_x_at_max_y):
            max_y = y
            min_x_at_max_y = x
            idx_left_top = i
    return idx_left_bottom, idx_left_top


def convexpoly_left_right(points: List[Tuple[float, float]]):
    """
    Build left and right sides of a convex polygon. Return them as lists of points.

    :param points: Points of a convex polygon
    :type points: List[Tuple[float, float]]
    """
    if not points:
        return [], []

    idx_left_bottom, idx_left_top = find_idx_left_bottom_and_top(points)

    if idx_left_bottom < idx_left_top:
        side_a = points[idx_left_bottom : idx_left_top + 1]
        side_b = points[idx_left_top:] + points[1 : idx_left_bottom + 1]
    else:
        side_a = points[idx_left_bottom:] + points[1 : idx_left_top + 1]
        side_b = points[idx_left_top : idx_left_bottom + 1]

    side_b.reverse()

    if side_a[1][0] < side_b[1][0]:
        return side_a, side_b
    else:
        return side_b, side_a


class SideSegmentInterpolator:
    """
    Class that represents a segment of a side of a convex polygon.
    Objects are stateful. The method x_at_y must be called in increasing order of y.
    The object is stateful. If it has to be called multiple times, do use `restart()`
    """

    def __init__(self, side: List[Tuple]):
        self.side = side
        self.segment_idx = -1
        self.segment_end_y = -1e9  # lowest possible y in any coordinate system
        self.coef = 0.0
        self.base = 0.0

    def x_at_y(self, y):
        if y > self.segment_end_y:
            searching = True
            while searching:
                self.segment_idx += 1
                self.segment_end_y = self.side[self.segment_idx + 1][1]
                pt_a = self.side[self.segment_idx]
                pt_b = self.side[self.segment_idx + 1]
                # Continue searching if the segment is horizontal (occurs only on right segment)
                searching = pt_a[1] == pt_b[1]
            # ...
            self.coef = (pt_b[0] - pt_a[0]) / (pt_b[1] - pt_a[1])
            self.base = pt_a[1] - self.coef * pt_a[0]

        return y * self.coef + self.base

    def restart(self):
        self.segment_idx = -1
        self.segment_end_y = -1e9
