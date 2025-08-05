from math import asin, atan2, cos, degrees, radians, sin

from microtyping import List, Tuple

# Average radius of the Earth in meters
R = const(6371008.8)


# Projects a point from lat/lon on the great circle with azimuth alpha (in degrees)
# at a distance (in meters)
def wgs84_project_xy(lon: float, lat: float, azimuth: float, distance: float):
    """
    Projects a point from latitude/longitude along a great circle path with a given azimuth and distance.

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


def wgs84_project(pt: Tuple[float, float], azimuth: float, distance: float) -> Tuple[float, float]:
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


def calc_bbox(coords: List[Tuple[float, float]]) -> Tuple[float, float, float, float]:
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
        if lon < min_lon:  # pylint: disable=consider-using-min-builtin
            min_lon = lon
        if lon > max_lon:  # pylint: disable=consider-using-max-builtin
            max_lon = lon
        if lat < min_lat:  # pylint: disable=consider-using-min-builtin
            min_lat = lat
        if lat > max_lat:  # pylint: disable=consider-using-max-builtin
            max_lat = lat

    return min_lon, min_lat, max_lon, max_lat
