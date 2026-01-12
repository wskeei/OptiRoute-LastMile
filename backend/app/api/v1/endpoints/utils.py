from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Any
from app.db.session import get_db
from app.models import all_models as models
import random

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
    # 1. Check if station exists
    station = db.query(models.DeliveryStation).first()
    if not station:
        station = models.DeliveryStation(
            name="Shanghai Center Station",
            address="People's Square, Shanghai",
            latitude=31.2304,
            longitude=121.4737
        )
        db.add(station)
        db.commit()
        db.refresh(station)

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
        for i in range(100):
            # Random lat/lon within ~10km
            lat_offset = (random.random() - 0.5) * 0.1
            lon_offset = (random.random() - 0.5) * 0.1
            
            pkg = models.Package(
                tracking_number=f"PKG{i:04d}",
                recipient_name=f"User {i}",
                recipient_phone="13900000000",
                recipient_address=f"Address {i}",
                latitude=station.latitude + lat_offset,
                longitude=station.longitude + lon_offset,
                status=models.PackageStatus.PENDING
            )
            packages.append(pkg)
        db.add_all(packages)
        db.commit()

    return {"message": "Data seeded successfully", "station_id": station.id}
