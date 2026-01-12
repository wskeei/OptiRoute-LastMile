import json
from typing import List
from sqlalchemy.orm import Session
from app.models import all_models as models
from app.schemas import all_schemas as schemas
from app.core.algorithms.kmeans import ConstrainedKMeans
from app.core.algorithms.genetic import GeneticAlgorithmTSP
from math import radians, cos, sin, asin, sqrt

# Route colors for visualization
ROUTE_COLORS = ['#667eea', '#48bb78', '#ed8936', '#f56565', '#9f7aea']

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two coordinates in kilometers using Haversine formula"""
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Earth radius in kilometers
    return c * r

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
            
            # 2. 执行 K-Means 聚类 (带容量约束)
            recipient_coords = [(p.latitude, p.longitude) for p in packages]
            weights = [getattr(p, 'weight', 1.0) or 1.0 for p in packages] # Ensure weight is not None
            depot_coord = (station.latitude, station.longitude)
            
            # 获取快递员容量
            courier_capacities = [c.max_capacity if c.max_capacity else 50.0 for c in couriers]

            kmeans = ConstrainedKMeans(k=k, max_distance_from_depot=50.0)
            kmeans.fit(recipient_coords, depot_coord, weights=weights, courier_capacities=courier_capacities)
            clusters = kmeans.get_clusters(recipient_coords)

            # 更新计划状态：K-Means 完成
            plan.algorithm_meta = {
                "step": "k_means_done",
                "clusters": clusters
            }
            self.db.commit()

            # 3. 对每个聚类执行 GA 路径优化并分配快递员
            temp_routes = {} # cluster_idx -> route_obj

            for cluster_idx, pkg_indices in clusters.items():
                if not pkg_indices:
                    continue

                # ... (Pre-create route object to allow updates)
                courier = couriers[cluster_idx] if cluster_idx < len(couriers) else None
                
                route = models.DeliveryRoute(
                    plan_id=plan.id,
                    courier_id=courier.id if courier else None,
                    geo_json={"status": "calculating"},
                    total_distance=0.0
                )
                self.db.add(route)
                self.db.flush() 
                temp_routes[cluster_idx] = route

            self.db.commit() # Commit so routes allow updates

            for cluster_idx, pkg_indices in clusters.items():
                if not pkg_indices:
                    continue

                cluster_packages = [packages[i] for i in pkg_indices]
                cluster_coords = [recipient_coords[i] for i in pkg_indices]
                cluster_center_lat = sum(coord[0] for coord in cluster_coords) / len(cluster_coords)
                cluster_center_lon = sum(coord[1] for coord in cluster_coords) / len(cluster_coords)
                
                route = temp_routes[cluster_idx]

                # 定义回调函数来更新进度
                def ga_progress_callback(generation, best_route_indices, best_fitness):
                     # 构建临时路径
                     temp_ordered_packages = [cluster_packages[i] for i in best_route_indices]
                     temp_coords = [depot_coord] + [(p.latitude, p.longitude) for p in temp_ordered_packages] + [depot_coord]
                     
                     total_dist = 0.0
                     for i in range(len(temp_coords) - 1):
                        total_dist += haversine_distance(temp_coords[i][0], temp_coords[i][1], temp_coords[i+1][0], temp_coords[i+1][1])

                     route.geo_json = {
                        "type": "LineString",
                        "coordinates": [[lon, lat] for lat, lon in temp_coords],
                        "cluster_center": [cluster_center_lat, cluster_center_lon],
                        "total_distance_km": round(total_dist, 2),
                        "package_count": len(temp_ordered_packages),
                        "color": ROUTE_COLORS[cluster_idx % len(ROUTE_COLORS)],
                        "generation": generation,
                        "status": "optimizing"
                     }
                     # 频繁 commit 会影响性能，但为了演示效果...
                     # 实际上应该用 Redis 或 WebSocket，这里简化直接写库
                     # 只在特定代数 commit?
                     if generation % 20 == 0:
                        self.db.commit()

                # 执行 GA-TSP
                ga = GeneticAlgorithmTSP(population_size=50, generations=100)
                best_route_indices, _ = ga.solve(cluster_coords, depot_coord, progress_callback=ga_progress_callback)

                # 更新最终结果
                ordered_packages = []
                for local_idx in best_route_indices:
                    pkg = cluster_packages[local_idx]
                    pkg.route_id = route.id
                    pkg.status = models.PackageStatus.ASSIGNED
                    ordered_packages.append(pkg)

                route_coords = [depot_coord] + [(p.latitude, p.longitude) for p in ordered_packages] + [depot_coord]
                
                final_total_distance = 0.0
                for i in range(len(route_coords) - 1):
                    final_total_distance += haversine_distance(route_coords[i][0], route_coords[i][1], route_coords[i+1][0], route_coords[i+1][1])

                route.geo_json = {
                    "type": "LineString",
                    "coordinates": [[lon, lat] for lat, lon in route_coords],
                    "cluster_center": [cluster_center_lat, cluster_center_lon],
                    "total_distance_km": round(final_total_distance, 2),
                    "package_count": len(ordered_packages),
                    "color": ROUTE_COLORS[cluster_idx % len(ROUTE_COLORS)],
                    "status": "optimized"
                }
                route.total_distance = final_total_distance
                self.db.commit()
                
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
