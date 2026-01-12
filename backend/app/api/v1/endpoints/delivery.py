from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models import all_models as models
from app.schemas import all_schemas as schemas

router = APIRouter()

# --- Station API ---

@router.post("/stations", response_model=schemas.Station)
def create_station(station: schemas.StationCreate, db: Session = Depends(get_db)):
    db_station = models.DeliveryStation(**station.model_dump())
    db.add(db_station)
    db.commit()
    db.refresh(db_station)
    return db_station

@router.get("/stations", response_model=List[schemas.Station])
def read_stations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.DeliveryStation).offset(skip).limit(limit).all()

# --- Courier API ---

@router.post("/couriers", response_model=schemas.Courier)
def create_courier(courier: schemas.CourierCreate, db: Session = Depends(get_db)):
    db_courier = models.Courier(**courier.model_dump())
    db.add(db_courier)
    db.commit()
    db.refresh(db_courier)
    return db_courier

@router.get("/couriers", response_model=List[schemas.Courier])
def read_couriers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Courier).offset(skip).limit(limit).all()

# --- Package API ---

@router.post("/packages", response_model=schemas.Package)
def create_package(package: schemas.PackageCreate, db: Session = Depends(get_db)):
    db_package = models.Package(**package.model_dump())
    db.add(db_package)
    db.commit()
    db.refresh(db_package)
    return db_package

@router.get("/packages", response_model=List[schemas.Package])
def read_packages(
    status: models.PackageStatus = Query(None),
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    query = db.query(models.Package)
    if status:
        query = query.filter(models.Package.status == status)
    return query.offset(skip).limit(limit).all()

@router.post("/packages/batch", response_model=List[schemas.Package])
def batch_create_packages(packages: List[schemas.PackageCreate], db: Session = Depends(get_db)):
    db_packages = [models.Package(**p.model_dump()) for p in packages]
    db.add_all(db_packages)
    db.commit()
    for p in db_packages:
        db.refresh(p)
    return db_packages
