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


def test_choose_random_station_seed_returns_city_level_station():
    station = choose_random_station_seed(seed=7)

    assert station["name"]
    assert station["address"]
    assert isinstance(station["latitude"], float)
    assert isinstance(station["longitude"], float)
