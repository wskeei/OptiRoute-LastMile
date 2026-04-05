from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import List
from app.db.session import get_db
from app.schemas import all_schemas as schemas
from app.models import all_models as models
from app.services.demo_data_service import (
    DEFAULT_DEMO_COURIER_COUNT,
    DEFAULT_DEMO_PACKAGE_COUNT,
    build_package_points_around_station,
    build_demo_courier_profiles,
    choose_random_station_seed,
)
from app.services.dispatch_service import DispatchService, run_dispatch_background
from app.services.station_service import StationService

router = APIRouter()


def _ensure_demo_packages(
    db: Session,
    *,
    station_payload: dict,
    target_count: int,
) -> list[models.Package]:
    import random

    packages = db.query(models.Package).order_by(models.Package.id.asc()).all()
    missing_count = target_count - len(packages)
    if missing_count > 0:
        package_points = build_package_points_around_station(
            station_payload,
            count=missing_count,
        )
        new_packages = []
        for i, package_point in enumerate(package_points):
            new_packages.append(
                models.Package(
                    tracking_number=f"DEMO{len(packages) + i + 1:06d}{random.randint(100, 999)}",
                    recipient_name=package_point["recipient_name"],
                    recipient_phone=f"138{random.randint(10000000, 99999999)}",
                    recipient_address=package_point["recipient_address"],
                    latitude=package_point["latitude"],
                    longitude=package_point["longitude"],
                    weight=round(random.uniform(0.5, 5.0), 1),
                    volume=round(random.uniform(0.01, 0.2), 2),
                    status=models.PackageStatus.ASSIGNED,
                )
            )
        db.add_all(new_packages)
        db.commit()
        packages = db.query(models.Package).order_by(models.Package.id.asc()).all()
    return packages


def _ensure_demo_couriers(
    db: Session,
    *,
    station_id: int,
    target_count: int,
) -> list[models.Courier]:
    couriers = db.query(models.Courier).order_by(models.Courier.id.asc()).all()
    missing_count = target_count - len(couriers)
    if missing_count > 0:
        courier_profiles = build_demo_courier_profiles(station_id, missing_count)
        new_couriers = [
            models.Courier(
                name=profile["name"],
                phone=profile["phone"],
                station_id=profile["station_id"],
                status=models.CourierStatus.OFF_DUTY,
            )
            for profile in courier_profiles
        ]
        db.add_all(new_couriers)
        db.commit()
        couriers = db.query(models.Courier).order_by(models.Courier.id.asc()).all()
    return couriers

@router.post("/plans", response_model=schemas.Plan)
def create_dispatch_plan(
    plan: schemas.PlanCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    创建并触发智能调度计划
    """
    service = DispatchService(db)

    # 1. 验证站点
    station = db.query(models.DeliveryStation).filter(models.DeliveryStation.id == plan.station_id).first()
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    # 2. 创建计划记录
    db_plan = service.create_optimization_plan(plan.title, plan.station_id)

    # 3. 触发后台计算任务
    background_tasks.add_task(run_dispatch_background, db_plan.id)

    return db_plan

@router.get("/plans", response_model=List[schemas.Plan])
def list_dispatch_plans(db: Session = Depends(get_db)):
    """
    获取所有调度计划历史
    """
    plans = db.query(models.DeliveryPlan).order_by(models.DeliveryPlan.created_at.desc()).all()
    return plans

@router.get("/plans/{plan_id}", response_model=schemas.Plan)
def get_dispatch_plan(plan_id: int, db: Session = Depends(get_db)):
    """
    获取调度计划详情（包含生成的路线）
    """
    db_plan = db.query(models.DeliveryPlan).filter(models.DeliveryPlan.id == plan_id).first()
    if not db_plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return db_plan

@router.get("/plans/{plan_id}/routes", response_model=List[schemas.Route])
def get_plan_routes(plan_id: int, db: Session = Depends(get_db)):
    """
    获取某个计划的所有路线详情
    """
    plan = db.query(models.DeliveryPlan).filter(models.DeliveryPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    routes = db.query(models.DeliveryRoute).filter(models.DeliveryRoute.plan_id == plan_id).all()
    return routes

@router.delete("/plans/all")
def clear_dispatch_history(db: Session = Depends(get_db)):
    """
    清空所有调度历史：
    1. 删除所有路线
    2. 删除所有计划
    3. 重置所有包裹状态为 PENDING (待配送)
    4. 重置所有快递员状态为 AVAILABLE (空闲)
    """
    try:
        # 1. Delete all routes
        db.query(models.DeliveryRoute).delete()
        
        # 2. Delete all plans
        db.query(models.DeliveryPlan).delete()
        
        # 3. Reset package status
        db.query(models.Package).update({
            "status": models.PackageStatus.PENDING,
            "route_id": None
        })
        
        # 4. Reset courier status
        db.query(models.Courier).update({
            "status": models.CourierStatus.AVAILABLE,
            "current_load": 0.0
        })
        
        db.commit()
        return {"message": "All history cleared successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reset-demo")
def reset_demo_data(payload: schemas.ResetDemoRequest, db: Session = Depends(get_db)):
    """
    重置演示数据：
    - 随机抽取100-150个包裹设为PENDING状态
    - 随机抽取5-10个快递员设为AVAILABLE状态
    """
    import random

    station_service = StationService(db)
    station = station_service.get_or_create_main_station()
    if payload.randomize_station:
        station = station_service.update_main_station(**choose_random_station_seed())

    station_payload = {
        "id": station.id,
        "name": station.name,
        "address": station.address,
        "latitude": station.latitude,
        "longitude": station.longitude,
    }

    all_packages = _ensure_demo_packages(
        db,
        station_payload=station_payload,
        target_count=DEFAULT_DEMO_PACKAGE_COUNT,
    )
    package_points = build_package_points_around_station(
        station_payload,
        count=len(all_packages),
    )
    for pkg, package_point in zip(all_packages, package_points):
        pkg.status = models.PackageStatus.ASSIGNED
        pkg.route_id = None
        pkg.weight = round(random.uniform(0.5, 8.0), 1)
        pkg.volume = round(random.uniform(0.01, 0.2), 2)
        pkg.recipient_name = package_point["recipient_name"]
        pkg.recipient_phone = f"138{random.randint(10000000, 99999999)}"
        pkg.recipient_address = package_point["recipient_address"]
        pkg.latitude = package_point["latitude"]
        pkg.longitude = package_point["longitude"]
    db.commit()

    all_package_ids = [pkg.id for pkg in all_packages]
    package_sample_size = min(random.randint(100, 150), len(all_package_ids))
    selected_package_ids = random.sample(all_package_ids, package_sample_size)
    for pkg in all_packages:
        if pkg.id in selected_package_ids:
            pkg.status = models.PackageStatus.PENDING
    db.commit()

    all_couriers = _ensure_demo_couriers(
        db,
        station_id=station.id,
        target_count=DEFAULT_DEMO_COURIER_COUNT,
    )
    for courier in all_couriers:
        courier.status = models.CourierStatus.OFF_DUTY
        courier.station_id = station.id
        courier.current_load = 0.0
    db.commit()

    # Calculate total weight of selected packages
    selected_packages = db.query(models.Package).filter(models.Package.id.in_(selected_package_ids)).all()
    total_package_weight = sum([p.weight for p in selected_packages])

    # 4. 随机抽取初始 5-10 个快递员
    all_courier_ids = [c.id for c in all_couriers]
    
    courier_sample_size = random.randint(5, 10)
    selected_courier_ids = random.sample(all_courier_ids, min(courier_sample_size, len(all_courier_ids)))

    # Activate them and assign random capacity
    total_courier_capacity = 0.0
    active_couriers = []
    
    # Calculate smart capacity based on expected average load
    # To keep it "tight", we want capacity to be just slightly above the average load
    num_couriers = len(selected_courier_ids)
    if num_couriers > 0:
        expected_avg_load = total_package_weight / num_couriers
    else:
        expected_avg_load = 50.0

    for c_id in selected_courier_ids:
        courier = db.query(models.Courier).filter(models.Courier.id == c_id).first()
        courier.status = models.CourierStatus.AVAILABLE
        
        # Set capacity to 1.1x - 1.4x of expected average load
        # This ensures utilization is high (around 70-90%) but leaves a safety buffer
        smart_capacity = expected_avg_load * random.uniform(1.1, 1.4)
        
        # Ensure a sane minimum (e.g. at least 30kg)
        courier.max_capacity = round(max(30.0, smart_capacity), 1)
        
        total_courier_capacity += courier.max_capacity
        active_couriers.append(courier)

    # 5. Ensure Solvability: Add more couriers if capacity is insufficient
    # Target: Total Capacity >= Total Weight * 1.15 (Tighten buffer to 15%)
    target_capacity = total_package_weight * 1.15
    
    remaining_courier_ids = list(set(all_courier_ids) - set(selected_courier_ids))
    
    while total_courier_capacity < target_capacity:
        if remaining_courier_ids:
            # Add another courier
            new_id = remaining_courier_ids.pop()
            new_courier = db.query(models.Courier).filter(models.Courier.id == new_id).first()
            new_courier.status = models.CourierStatus.AVAILABLE
            new_courier.max_capacity = round(random.uniform(120.0, 200.0), 1) # Give higher capacity to help
            total_courier_capacity += new_courier.max_capacity
            active_couriers.append(new_courier)
        else:
            # No more couriers, boost existing capacities
            for c in active_couriers:
                boost = 50.0
                c.max_capacity += boost
                total_courier_capacity += boost
                if total_courier_capacity >= target_capacity:
                    break
    
    db.commit()

    pending_count = db.query(models.Package).filter(models.Package.status == models.PackageStatus.PENDING).count()
    available_couriers = db.query(models.Courier).filter(models.Courier.status == models.CourierStatus.AVAILABLE).count()
    total_packages = db.query(models.Package).count()
    total_couriers = db.query(models.Courier).count()

    return {
        "message": "Demo data reset successfully",
        "pending_packages": pending_count,
        "total_packages": total_packages,
        "available_couriers": available_couriers,
        "total_couriers": total_couriers,
        "station": station_payload,
    }
