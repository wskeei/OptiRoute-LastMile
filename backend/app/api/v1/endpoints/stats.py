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
    """返回快递员排行榜（基于历史累计分配包裹数）"""
    # 获取所有非空闲且已完成或就绪的计划中的路线，或者所有路线更简单（历史记录）
    routes = db.query(models.DeliveryRoute).filter(
        models.DeliveryRoute.courier_id.isnot(None)
    ).all()

    courier_stats = {}
    
    for route in routes:
        cid = route.courier_id
        # 从 geo_json 中获取当时分配的包裹数
        # 如果是旧数据没有 geo_json，尝试用 packages 关联（但可能已断开）
        # 我们主要依赖 geo_json
        count = 0
        if route.geo_json and 'package_count' in route.geo_json:
            count = route.geo_json['package_count']
        
        if cid not in courier_stats:
            courier_stats[cid] = 0
        courier_stats[cid] += count

    # 获取快递员名称
    courier_ids = list(courier_stats.keys())
    couriers = db.query(models.Courier).filter(models.Courier.id.in_(courier_ids)).all()
    courier_map = {c.id: c.name for c in couriers}

    ranking = []
    for cid, count in courier_stats.items():
        ranking.append({
            "id": cid,
            "name": courier_map.get(cid, f"快递员{cid}"),
            "delivered_count": count
        })

    # 排序并取前10
    ranking.sort(key=lambda x: x["delivered_count"], reverse=True)
    return ranking[:10]
