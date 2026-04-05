import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.session import get_db
from app.models.all_models import Base, Package, Courier, DeliveryStation, PackageStatus, CourierStatus
from app.api.v1.endpoints import dispatch as dispatch_endpoint

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def test_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    station = DeliveryStation(name="测试站点", address="上海市浦东新区", latitude=31.2304, longitude=121.4737)
    db.add(station)
    db.commit()

    for i in range(10):
        pkg = Package(
            tracking_number=f"TEST{i:04d}",
            recipient_name=f"测试用户{i}",
            recipient_phone="13800138000",
            recipient_address=f"上海市浦东新区测试路{i}号",
            latitude=31.2304 + i * 0.01,
            longitude=121.4737 + i * 0.01,
            status=PackageStatus.PENDING
        )
        db.add(pkg)

    for i in range(3):
        courier = Courier(
            name=f"测试快递员{i}",
            phone=f"1380013800{i}",
            status=CourierStatus.AVAILABLE,
            station_id=1
        )
        db.add(courier)

    db.commit()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def background_runner_spy(monkeypatch):
    calls = []

    def fake_run_dispatch_background(plan_id: int):
        calls.append(plan_id)

    monkeypatch.setattr(dispatch_endpoint, "run_dispatch_background", fake_run_dispatch_background)
    return calls

client = TestClient(app)

def test_create_dispatch_plan(test_db, background_runner_spy):
    response = client.post("/api/v1/dispatch/plans", json={
        "title": "测试调度计划",
        "station_id": 1,
        "algorithm_meta": {"k": 3, "generations": 100}
    })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "测试调度计划"
    assert data["station_id"] == 1
    assert data["status"] in ["PENDING", "OPTIMIZING"]
    assert background_runner_spy == [data["id"]]

def test_list_dispatch_plans(test_db, background_runner_spy):
    client.post("/api/v1/dispatch/plans", json={
        "title": "测试计划1",
        "station_id": 1,
        "algorithm_meta": {"k": 3, "generations": 100}
    })

    response = client.get("/api/v1/dispatch/plans")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["title"] == "测试计划1"

def test_get_dispatch_plan(test_db, background_runner_spy):
    create_response = client.post("/api/v1/dispatch/plans", json={
        "title": "测试计划详情",
        "station_id": 1,
        "algorithm_meta": {"k": 3, "generations": 100}
    })
    plan_id = create_response.json()["id"]

    response = client.get(f"/api/v1/dispatch/plans/{plan_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == plan_id
    assert data["title"] == "测试计划详情"

def test_get_plan_routes(test_db, background_runner_spy):
    create_response = client.post("/api/v1/dispatch/plans", json={
        "title": "测试路线",
        "station_id": 1,
        "algorithm_meta": {"k": 3, "generations": 100}
    })
    plan_id = create_response.json()["id"]

    response = client.get(f"/api/v1/dispatch/plans/{plan_id}/routes")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_reset_demo_data(test_db):
    response = client.post("/api/v1/dispatch/reset-demo", json={"randomize_station": False})
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert 100 <= data["pending_packages"] <= 150
    assert data["total_packages"] >= 300
    assert data["total_couriers"] >= 10
    assert "station" in data


def test_reset_demo_data_creates_usable_samples_when_only_station_exists(test_db):
    test_db.query(Package).delete()
    test_db.query(Courier).delete()
    test_db.commit()

    response = client.post("/api/v1/dispatch/reset-demo", json={"randomize_station": False})

    assert response.status_code == 200
    data = response.json()
    assert data["pending_packages"] > 0
    assert data["available_couriers"] > 0
    assert test_db.query(Package).count() > 0
    assert test_db.query(Courier).count() > 0


def test_reset_demo_data_can_randomize_main_station(test_db):
    response = client.post("/api/v1/dispatch/reset-demo", json={"randomize_station": True})

    assert response.status_code == 200
    data = response.json()
    assert "station" in data
    assert "latitude" in data["station"]
    assert "longitude" in data["station"]

def test_create_plan_invalid_station(test_db):
    response = client.post("/api/v1/dispatch/plans", json={
        "title": "无效站点",
        "station_id": 999,
        "algorithm_meta": {"k": 3, "generations": 100}
    })
    assert response.status_code == 404

def test_get_nonexistent_plan(test_db):
    response = client.get("/api/v1/dispatch/plans/999")
    assert response.status_code == 404
