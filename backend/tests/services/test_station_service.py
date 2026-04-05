from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models.all_models import Base, DeliveryPlan, DeliveryStation, PlanStatus
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


def test_update_main_station_preserves_existing_plan_station_context():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        station = DeliveryStation(
            name="上海人民广场配送站",
            address="上海市黄浦区人民广场",
            latitude=31.2304,
            longitude=121.4737,
        )
        db.add(station)
        db.commit()
        db.refresh(station)

        plan = DeliveryPlan(
            title="历史计划",
            station_id=station.id,
            status=PlanStatus.COMPLETED,
            algorithm_meta={},
        )
        db.add(plan)
        db.commit()
        db.refresh(plan)

        updated_station = StationService(db).update_main_station(
            name="成都春熙路配送站",
            address="成都市锦江区春熙路",
            latitude=30.6586,
            longitude=104.0817,
        )
        db.refresh(plan)

        assert updated_station.name == "成都春熙路配送站"
        assert plan.station_id != updated_station.id
        assert plan.station.name == "上海人民广场配送站"
        assert plan.station.address == "上海市黄浦区人民广场"
        assert plan.station.latitude == 31.2304
        assert plan.station.longitude == 121.4737
    finally:
        db.close()
