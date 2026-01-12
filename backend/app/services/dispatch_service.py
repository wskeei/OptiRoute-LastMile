import json
from typing import List
from sqlalchemy.orm import Session
from app.models import all_models as models
from app.schemas import all_schemas as schemas
from app.core.algorithms.kmeans import ConstrainedKMeans
from app.core.algorithms.genetic import GeneticAlgorithmTSP

class DispatchService:
    def __init__(self, db: Session):
        self.db = db

    def create_optimization_plan(self, title: str, station_id: int) -> models.DeliveryPlan:
        """创建一个新的配送计划（初始状态）"""
        plan = models.DeliveryPlan(
            title=title,
            station_id=station_id,
            status=models.PlanStatus.OPTIMIZING,
            algorithm_meta={"k_means": {}, "ga": {}}
        )
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)
        return plan

    def run_dispatch_algorithm(self, plan_id: int):
        """
        核心调度逻辑（应在后台运行）
        1. 获取数据
        2. K-Means 聚类
        3. GA 路径优化
        4. 保存结果
        """
        # 重新获取 plan (确保在当前 session)
        plan = self.db.query(models.DeliveryPlan).filter(models.DeliveryPlan.id == plan_id).first()
        if not plan:
            return

        try:
            # 1. 准备数据
            station = plan.station
            if not station:
                raise ValueError(f"Station not found for plan {plan_id}")

            # 获取该站点下待分配的包裹
            # 注意：实际生产中可能需要更复杂的筛选逻辑（例如根据创建时间）
            packages = self.db.query(models.Package).filter(
                models.Package.status == models.PackageStatus.PENDING
                # 这里可以加更多过滤，比如距离筛选
            ).all()

            # 获取可用快递员
            couriers = self.db.query(models.Courier).filter(
                models.Courier.station_id == station.id,
                models.Courier.status == models.CourierStatus.AVAILABLE
            ).all()

            num_packages = len(packages)
            num_couriers = len(couriers)

            if num_packages == 0:
                plan.status = models.PlanStatus.COMPLETED
                plan.algorithm_meta = {"error": "No pending packages found"}
                self.db.commit()
                return

            if num_couriers == 0:
                plan.status = models.PlanStatus.COMPLETED
                plan.algorithm_meta = {"error": "No available couriers found"}
                self.db.commit()
                return

            # K值取快递员数量，但不能超过包裹数
            k = min(num_couriers, num_packages)
            
            # 2. 执行 K-Means 聚类
            recipient_coords = [(p.latitude, p.longitude) for p in packages]
            depot_coord = (station.latitude, station.longitude)

            kmeans = ConstrainedKMeans(k=k, max_distance_from_depot=50.0)
            kmeans.fit(recipient_coords, depot_coord)
            clusters = kmeans.get_clusters(recipient_coords)

            # 3. 对每个聚类执行 GA 路径优化并分配快递员
            # 简单的分配策略：按顺序分配（更高级的策略是考虑快递员当前负载或位置）
            
            for cluster_idx, pkg_indices in clusters.items():
                if not pkg_indices:
                    continue
                
                # 获取该聚类的包裹对象
                cluster_packages = [packages[i] for i in pkg_indices]
                cluster_coords = [recipient_coords[i] for i in pkg_indices]
                
                # 执行 GA-TSP
                ga = GeneticAlgorithmTSP(population_size=50, generations=100) # 快速版参数
                best_route_indices, _ = ga.solve(cluster_coords, depot_coord)
                
                # 计算总距离 (fitness 是 1/distance)
                # 重新计算一遍确切距离
                # 注意：best_route_indices 是局部索引 (0 到 len(cluster)-1)
                
                # 构建 DeliveryRoute
                courier = couriers[cluster_idx] if cluster_idx < len(couriers) else None
                
                route = models.DeliveryRoute(
                    plan_id=plan.id,
                    courier_id=courier.id if courier else None,
                    geo_json={"indices": best_route_indices}, # 实际应存储完整 GeoJSON
                    total_distance=0.0 # 暂未精确计算
                )
                self.db.add(route)
                self.db.flush() # 获取 route.id
                
                # 更新包裹状态并关联路线
                ordered_packages = []
                for local_idx in best_route_indices:
                    pkg = cluster_packages[local_idx]
                    pkg.route_id = route.id
                    pkg.status = models.PackageStatus.ASSIGNED
                    ordered_packages.append(pkg)
                
                # 这里可以基于 Ordered packages 重新生成 GeoJSON 包含坐标序列
                route_coords = [depot_coord] + [(p.latitude, p.longitude) for p in ordered_packages] + [depot_coord]
                route.geo_json = {
                    "type": "LineString",
                    "coordinates": [[lon, lat] for lat, lon in route_coords] # GeoJSON uses [lon, lat]
                }
                
            # 4. 完成
            plan.status = models.PlanStatus.READY
            self.db.commit()

        except Exception as e:
            print(f"Algorithm Error: {e}")
            self.db.rollback()
            plan.status = models.PlanStatus.DRAFT # Reset or Error status
            plan.algorithm_meta = {"error": str(e)}
            self.db.commit()

def run_dispatch_background(plan_id: int):
    """
    FastAPI BackgroundTasks 的入口函数
    """
    # 需要手动创建新的 DB Session，因为 BackgroundTasks 在请求结束后运行
    from app.db.session import SessionLocal
    db = SessionLocal()
    try:
        service = DispatchService(db)
        service.run_dispatch_algorithm(plan_id)
    finally:
        db.close()
