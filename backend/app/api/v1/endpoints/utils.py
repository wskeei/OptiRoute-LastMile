from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Any
from app.db.session import get_db
from app.models import all_models as models
from app.services.demo_data_service import build_package_points_around_station
from app.services.station_service import StationService

router = APIRouter()

@router.get("/health-check")
def health_check() -> Any:
    """
    Check if the API is alive.
    """
    return {"status": "ok"}

@router.post("/seed-data")
def seed_data(db: Session = Depends(get_db)) -> Any:
    """
    Seed database with test data:
    - 1 Station (Shanghai)
    - 5 Couriers
    - 100 Random Packages
    """
    station = StationService(db).get_or_create_main_station()

    # 2. Seed Couriers
    if db.query(models.Courier).count() == 0:
        couriers = [
            models.Courier(name=f"Courier {i+1}", phone=f"1380013800{i}", station_id=station.id, status=models.CourierStatus.AVAILABLE)
            for i in range(5)
        ]
        db.add_all(couriers)
        db.commit()

    # 3. Seed Packages (Random locations around station)
    if db.query(models.Package).count() < 10:
        packages = []
        package_points = build_package_points_around_station(
            {
                "name": station.name,
                "address": station.address,
                "latitude": station.latitude,
                "longitude": station.longitude,
            },
            count=100,
        )
        for i, package_point in enumerate(package_points):
            pkg = models.Package(
                tracking_number=f"PKG{i:04d}",
                recipient_name=package_point["recipient_name"],
                recipient_phone="13900000000",
                recipient_address=package_point["recipient_address"],
                latitude=package_point["latitude"],
                longitude=package_point["longitude"],
                status=models.PackageStatus.PENDING
            )
            packages.append(pkg)
        db.add_all(packages)
        db.commit()

    return {"message": "Data seeded successfully", "station_id": station.id}
