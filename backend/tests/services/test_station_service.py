from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models.all_models import Base, DeliveryStation
from app.services.station_service import DEFAULT_MAIN_STATION
from app.services.station_service import StationService


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def test_get_or_create_main_station_creates_default_when_missing():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        station = StationService(db).get_or_create_main_station()
        assert station.name == DEFAULT_MAIN_STATION["name"]
        assert station.address == DEFAULT_MAIN_STATION["address"]
        assert station.latitude == DEFAULT_MAIN_STATION["latitude"]
        assert station.longitude == DEFAULT_MAIN_STATION["longitude"]
    finally:
        db.close()


def test_get_or_create_main_station_returns_lowest_id_when_multiple_exist():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        db.add_all(
            [
                DeliveryStation(name="B", address="B", latitude=30.0, longitude=120.0),
                DeliveryStation(name="A", address="A", latitude=31.0, longitude=121.0),
            ]
        )
        db.commit()

        station = StationService(db).get_or_create_main_station()

        assert station.id == 1
    finally:
        db.close()
