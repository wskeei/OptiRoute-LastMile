from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.schemas import all_schemas as schemas
from app.models import all_models as models
from app.services.dispatch_service import DispatchService, run_dispatch_background

router = APIRouter()

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

@router.post("/reset-demo")
def reset_demo_data(db: Session = Depends(get_db)):
    """
    重置演示数据：
    - 随机抽取100-150个包裹设为PENDING状态
    - 随机抽取5-10个快递员设为AVAILABLE状态
    """
    import random

    # 1. 将所有包裹设为ASSIGNED状态
    db.query(models.Package).update({
        "status": models.PackageStatus.ASSIGNED,
        "route_id": None
    })
    db.commit()

    # 2. 随机抽取100-150个包裹设为PENDING
    all_packages = db.query(models.Package).all()
    all_package_ids = [pkg.id for pkg in all_packages]
    package_sample_size = random.randint(100, 150)
    selected_package_ids = random.sample(all_package_ids, min(package_sample_size, len(all_package_ids)))

    db.query(models.Package).filter(models.Package.id.in_(selected_package_ids)).update({
        "status": models.PackageStatus.PENDING
    }, synchronize_session=False)
    db.commit()

    # 3. 将所有快递员设为OFF_DUTY状态
    db.query(models.Courier).update({
        "status": models.CourierStatus.OFF_DUTY
    })
    db.commit()

    # 4. 随机抽取5-10个快递员设为AVAILABLE
    all_couriers = db.query(models.Courier).all()
    all_courier_ids = [c.id for c in all_couriers]
    courier_sample_size = random.randint(5, min(10, len(all_courier_ids)))
    selected_courier_ids = random.sample(all_courier_ids, courier_sample_size)

    db.query(models.Courier).filter(models.Courier.id.in_(selected_courier_ids)).update({
        "status": models.CourierStatus.AVAILABLE
    }, synchronize_session=False)
    db.commit()

    pending_count = db.query(models.Package).filter(models.Package.status == models.PackageStatus.PENDING).count()
    available_couriers = db.query(models.Courier).filter(models.Courier.status == models.CourierStatus.AVAILABLE).count()
    total_packages = len(all_package_ids)
    total_couriers = len(all_courier_ids)

    return {
        "message": "Demo data reset successfully",
        "pending_packages": pending_count,
        "total_packages": total_packages,
        "available_couriers": available_couriers,
        "total_couriers": total_couriers
    }
