from math import asin, cos, radians, sin, sqrt

from app.services.demo_data_service import (
    build_package_points_around_station,
    choose_random_station_seed,
)


def test_build_package_points_around_station_stays_near_station():
    station = {
        "name": "上海人民广场配送站",
        "address": "上海市黄浦区人民广场",
        "latitude": 31.2304,
        "longitude": 121.4737,
    }

    packages = build_package_points_around_station(station, count=50, seed=7)

    assert len(packages) == 50
    assert all("latitude" in pkg and "longitude" in pkg for pkg in packages)


def test_build_package_points_around_station_keeps_old_spread_feel():
    station = {
        "name": "上海人民广场配送站",
        "address": "上海市黄浦区人民广场",
        "latitude": 31.2304,
        "longitude": 121.4737,
    }

    packages = build_package_points_around_station(station, count=300, seed=7)

    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        return 6371 * 2 * asin(sqrt(a))

    distances = [
        haversine_distance(
            station["latitude"],
            station["longitude"],
            package["latitude"],
            package["longitude"],
        )
        for package in packages
    ]

    assert max(distances) > 12
    assert sum(distance >= 8 for distance in distances) >= 80


def test_choose_random_station_seed_returns_city_level_station():
    station = choose_random_station_seed(seed=7)

    assert station["name"]
    assert station["address"]
    assert isinstance(station["latitude"], float)
    assert isinstance(station["longitude"], float)
