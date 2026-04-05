import math
import random

from app.utils.china_station_catalog import CHINA_MAIN_STATION_SEEDS


DISTRICT_NAMES = ["核心区", "商圈片区", "居住片区", "园区片区", "滨江片区", "大学城片区"]
ROAD_NAMES = ["中山路", "解放路", "人民路", "建设路", "创新大道", "幸福街"]
DEFAULT_DEMO_PACKAGE_COUNT = 300
DEFAULT_DEMO_COURIER_COUNT = 10


def choose_random_station_seed(seed: int | None = None) -> dict:
    rng = random.Random(seed)
    return dict(rng.choice(CHINA_MAIN_STATION_SEEDS))


def _km_to_lat(km: float) -> float:
    return km / 111.0


def _km_to_lng(km: float, lat: float) -> float:
    cosine = math.cos(math.radians(lat))
    return km / (111.0 * max(abs(cosine), 1e-6))


def _extract_city_name(station: dict) -> str:
    address = station.get("address", "")
    if "市" in address:
        return address.split("市", 1)[0] + "市"
    return station.get("name", "")[:3] or "示例市"


def build_package_points_around_station(
    station: dict,
    count: int,
    seed: int | None = None,
) -> list[dict]:
    rng = random.Random(seed)
    anchors = []

    for _ in range(rng.randint(5, 8)):
        radius_km = rng.uniform(0.8, 6.0)
        angle = rng.uniform(0, math.pi * 2)
        anchors.append(
            (
                station["latitude"] + _km_to_lat(radius_km * math.cos(angle)),
                station["longitude"] + _km_to_lng(radius_km * math.sin(angle), station["latitude"]),
            )
        )

    city_name = _extract_city_name(station)
    packages = []

    for index in range(count):
        roll = rng.random()
        if roll < 0.65:
            radius_km = rng.uniform(0.8, 3.0)
        elif roll < 0.90:
            radius_km = rng.uniform(3.0, 8.0)
        else:
            radius_km = rng.uniform(8.0, 15.0)

        anchor_lat, anchor_lng = rng.choice(anchors)
        angle = rng.uniform(0, math.pi * 2)
        local_jitter_km = min(1.2, radius_km * 0.35)
        latitude = anchor_lat + _km_to_lat(local_jitter_km * math.cos(angle))
        longitude = anchor_lng + _km_to_lng(local_jitter_km * math.sin(angle), station["latitude"])
        district_name = rng.choice(DISTRICT_NAMES)
        road_name = rng.choice(ROAD_NAMES)
        building_no = rng.randint(1, 999)

        packages.append(
            {
                "recipient_name": f"演示用户{index + 1}",
                "recipient_address": f"{city_name}{district_name}{road_name}{building_no}号",
                "latitude": latitude,
                "longitude": longitude,
            }
        )

    return packages


def build_demo_courier_profiles(station_id: int, count: int) -> list[dict]:
    return [
        {
            "name": f"演示快递员{i + 1}",
            "phone": f"139{(i + 1):08d}",
            "station_id": station_id,
        }
        for i in range(count)
    ]
