from math import radians, degrees, sin, cos, asin, atan2
from macropython import *

# Average radius of the Earth in meters
R = const(6371008.8)

# Pprojects a point from lat/lon on the great circle with azimuth alpha (in degrees)
# at a distance (in meters)
def wgs84_project(lon, lat, azimuth, distance):
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
    taget_lon = lon + delta_lon

    # Convert the results to degrees
    target_lat = degrees(target_lat)
    taget_lon = degrees(taget_lon)

    return taget_lon, target_lat
