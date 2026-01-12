from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
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

@router.get("/plans/{plan_id}", response_model=schemas.Plan)
def get_dispatch_plan(plan_id: int, db: Session = Depends(get_db)):
    """
    获取调度计划详情（包含生成的路线）
    """
    db_plan = db.query(models.DeliveryPlan).filter(models.DeliveryPlan.id == plan_id).first()
    if not db_plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return db_plan
