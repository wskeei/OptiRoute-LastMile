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
    limit: int = 500,
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

@router.post("/packages/reinit")
def reinit_package_data(db: Session = Depends(get_db)):
    """
    重新初始化包裹数据：
    1. 清空所有现有包裹
    2. 重新生成 300 个上海真实地址的包裹
    """
    try:
        # 1. Clear existing packages
        # First clear route associations to avoid FK issues if any remain (though clear history handles this)
        db.query(models.Package).delete()
        db.commit()

        # 2. Seed new data
        import random
        from app.utils.seed_shanghai_data import get_shanghai_locations
        
        shanghai_locs = get_shanghai_locations() # 100 base locations
        
        # Determine how many to generate (user said 300)
        target_count = 300
        
        # Since we have only 100 base locations, we sample with replacement or jitter them
        # Let's simple sample with replacement for now, or loop
        
        new_packages = []
        for i in range(target_count):
            # Pick a random base location
            base_loc = random.choice(shanghai_locs)
            
            # Add slight jitter to coords to avoid perfect overlap
            jitter_lat = random.uniform(-0.005, 0.005)
            jitter_lon = random.uniform(-0.005, 0.005)
            
            pkg = models.Package(
                tracking_number=f"SF{random.randint(10000000, 99999999)}",
                recipient_name=f"{base_loc['recipient']}-{i+1}", # Unique-ish name
                recipient_phone=f"138{random.randint(10000000, 99999999)}",
                recipient_address=base_loc['address'],
                latitude=base_loc['lat'] + jitter_lat,
                longitude=base_loc['lng'] + jitter_lon,
                weight=round(random.uniform(0.5, 5.0), 1),
                volume=round(random.uniform(0.01, 0.2), 2),
                status=models.PackageStatus.PENDING
            )
            new_packages.append(pkg)
            
        db.add_all(new_packages)
        db.commit()
        
        return {"message": f"Successfully re-initialized {target_count} packages"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
