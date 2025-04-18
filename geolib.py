from math import radians, degrees, sin, cos, asin, atan2
from macropython import *

# Rayon moyen de la Terre en mètres
R = const(6371008.8)


# Comme wgs84_direct mais en plus rapide, c.-à-d. projète un point à partir de lat/lon sur
# l'orthodromie d'azimuth alpha (en degrée) à une distance r (en mètre)
def wgs84_project(lon, lat, cap, distance):
    # Convertir les valeurs initiales en radians
    lat = radians(lat)
    lon = radians(lon)
    cap = radians(cap)

    # Calculer la distance angulaire
    delta = distance / R

    # Calculer la latitude de B en radians
    lat_b = asin(sin(lat) * cos(delta) + cos(lat) * sin(delta) * cos(cap))

    # Calculer la différence de longitude en radians
    delta_lon = atan2(sin(cap) * sin(delta) * cos(lat), cos(delta) - sin(lat) * sin(lat_b))

    # Calculer la longitude de B
    lon_b = lon + delta_lon

    # Convertir les résultats en degrés
    lat_b = degrees(lat_b)
    lon_b = degrees(lon_b)

    return lon_b, lat_b
