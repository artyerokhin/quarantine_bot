import requests
import shutil
import json
import os

import geog
import numpy as np
import shapely.geometry


# keys must be in environment variabless
MAPS_API_KEY = os.environ.get("MAPS_API_KEY")
TELEGRAM_BOT_KEY = os.environ.get("TELEGRAM_BOT_KEY")


def circle_polygon(point, n_points=50, distance=100):
    """Create circle polygon for some point"""
    p = shapely.geometry.Point(point)
    angles = np.linspace(0, 360, n_points)
    polygon = geog.propagate(p, angles, distance)
    return json.dumps(shapely.geometry.mapping(shapely.geometry.Polygon(polygon)))


def concat_coordinates(coordinates):
    """Concat coordinates into string"""
    concat_lst = []
    for point in coordinates:
        concat_lst.append("{},{}".format(point[0], point[1]))
    return ",".join(concat_lst)


def generate_request(circle_json):
    """Generate request to Yandex.Maps static map API"""
    request = (
        """https://static-maps.yandex.ru/1.x/?l=map&pl=c:ec473fFF,f:24B20E30, w:1,{}"""
    )
    coordinates = json.loads(circle_json)["coordinates"][0]
    return request.format(concat_coordinates(coordinates))


def parse_response(response):
    """Parse geocoder responce"""
    if not response:
        return None
    else:
        try:
            point = response.json()["response"]["GeoObjectCollection"]["featureMember"][
                0
            ]["GeoObject"]["Point"]["pos"].split(" ")
            return (float(point[0]), float(point[1]))
        except Exception as e:
            return None


def reverse_geocode_address(address):
    """Apply reverse geocoding to text address"""
    request = "https://geocode-maps.yandex.ru/1.x/?apikey={}&format=json&geocode={}"
    address = address.replace(" ", "+")
    response = requests.get(request.format(MAPS_API_KEY, address))
    return parse_response(response)


def generate_map(address, file_name=None):
    """Generate map for address"""
    point = reverse_geocode_address(address)

    if point:
        request = generate_request(circle_polygon(point))
        response = requests.get(request, stream=True)
        if file_name is None:
            file_name = "{}.png".format("{}_{}".format(point[0], point[1]))
        with open(file_name, "wb") as f:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, f)
        return True
    else:
        return False
