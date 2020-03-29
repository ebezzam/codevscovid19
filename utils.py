from math import sin, cos, sqrt, atan2, radians, degrees, sqrt


class Coordinate(object):
    def __init__(self, lon, lat, radius=6373.0):
        """
        R : approximate radius of earth in km
        """
        self.lon = lon
        self.lat = lat
        self.radius = radius

    def __sub__(self, other):
        """
        Get distance between two coordinates
        """
        lat1 = radians(self.lat)
        lon1 = radians(self.lon)
        lat2 = radians(other.lat)
        lon2 = radians(other.lon)

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return self.radius * c

    def bounding_box(self, max_dist):
        # https://stackoverflow.com/a/238558
        lat = radians(self.lat)
        lon = radians(self.lon)
        half_side = 1000 * max_dist

        # Radius of Earth at given latitude
        radius = WGS84EarthRadius(lat)
        # Radius of the parallel at given latitude
        pradius = radius * cos(lat)

        coord_max = Coordinate(
            lon=degrees(lon + half_side / pradius),
            lat=degrees(lat + half_side / radius)
        )
        coord_min = Coordinate(
            lon=degrees(lon - half_side / pradius),
            lat=degrees(lat - half_side / radius)
        )
        return coord_max, coord_min

    def print(self):
        print(f"Longitude : {self.lon}\nLatitude : {self.lat}")


# Earth radius at a given latitude, according to the WGS-84 ellipsoid [m]
# Semi-axes of WGS-84 geoidal reference
WGS84_a = 6378137.0  # Major semiaxis [m]
WGS84_b = 6356752.3  # Minor semiaxis [m]


def WGS84EarthRadius(lat):
    # http://en.wikipedia.org/wiki/Earth_radius
    An = WGS84_a * WGS84_a * cos(lat)
    Bn = WGS84_b * WGS84_b * sin(lat)
    Ad = WGS84_a * cos(lat)
    Bd = WGS84_b * sin(lat)
    return sqrt((An*An + Bn*Bn)/(Ad*Ad + Bd*Bd))


if __name__ == "__main__":
    coord1 = Coordinate(lon=21.0122287, lat=52.2296756)
    coord2 = Coordinate(lon=16.9251681, lat=52.406374)

    print(coord1 - coord2)

    # get bounding box
    coord_max, coord_min = coord1.bounding_box(max_dist=10)
    print("coordinate")
    coord1.print()
    print("max coordinate")
    coord_max.print()
    print("min coordinate")
    coord_min.print()
