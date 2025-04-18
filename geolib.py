from math import radians, degrees, sin, cos, asin, atan2
from macropython import *

# Average radius of the Earth in meters
R = const(6371008.8)

# Projects a point from lat/lon on the great circle with azimuth alpha (in degrees)
# at a distance (in meters)
def wgs84_project(lon, lat, azimuth, distance):
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

    # Calculate the latitude of target in radians
    target_lat = asin(sin(lat) * cos(delta) + cos(lat) * sin(delta) * cos(azimuth))

    # Calculate the longitude difference in radians
    delta_lon = atan2(sin(azimuth) * sin(delta) * cos(lat), cos(delta) - sin(lat) * sin(target_lat))

    # Calculate the longitude of target in radians
    target_lon = lon + delta_lon

    # Convert the results to degrees
    target_lat = degrees(target_lat)
    target_lon = degrees(target_lon)

    return target_lon, target_lat
