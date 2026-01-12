from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import get_db
from app.models import all_models as models

router = APIRouter()

@router.get("/dashboard")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """返回Dashboard需要的统计数据"""
    pending = db.query(models.Package).filter(models.Package.status == models.PackageStatus.PENDING).count()
    in_transit = db.query(models.Package).filter(models.Package.status == models.PackageStatus.IN_TRANSIT).count()
    completed = db.query(models.Package).filter(models.Package.status == models.PackageStatus.DELIVERED).count()
    online_couriers = db.query(models.Courier).filter(models.Courier.status == models.CourierStatus.AVAILABLE).count()

    return {
        "pending_count": pending,
        "in_transit_count": in_transit,
        "completed_count": completed,
        "online_couriers": online_couriers,
        "efficiency_improvement": 12.5
    }

@router.get("/courier-ranking")
def get_courier_ranking(db: Session = Depends(get_db)):
    """返回快递员排行榜"""
    couriers = db.query(
        models.Courier.id,
        models.Courier.name,
        func.count(models.Package.id).label('delivered_count')
    ).join(
        models.DeliveryRoute, models.Courier.id == models.DeliveryRoute.courier_id, isouter=True
    ).join(
        models.Package, models.DeliveryRoute.id == models.Package.route_id, isouter=True
    ).filter(
        models.Package.status == models.PackageStatus.DELIVERED
    ).group_by(models.Courier.id).order_by(func.count(models.Package.id).desc()).limit(10).all()

    return [{"id": c.id, "name": c.name, "delivered_count": c.delivered_count} for c in couriers]
