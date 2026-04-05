from sqlalchemy.orm import Session

from app.models import all_models as models


DEFAULT_MAIN_STATION = {
    "name": "上海人民广场配送站",
    "address": "上海市黄浦区人民广场",
    "latitude": 31.2304,
    "longitude": 121.4737,
}


class StationService:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_main_station(self) -> models.DeliveryStation:
        station = (
            self.db.query(models.DeliveryStation)
            .order_by(models.DeliveryStation.id.asc())
            .first()
        )
        if station:
            return station

        station = models.DeliveryStation(**DEFAULT_MAIN_STATION)
        self.db.add(station)
        self.db.commit()
        self.db.refresh(station)
        return station

    def update_main_station(
        self,
        *,
        name: str,
        address: str,
        latitude: float,
        longitude: float,
    ) -> models.DeliveryStation:
        station = self.get_or_create_main_station()
        station.name = name
        station.address = address
        station.latitude = latitude
        station.longitude = longitude
        self.db.commit()
        self.db.refresh(station)
        return station
