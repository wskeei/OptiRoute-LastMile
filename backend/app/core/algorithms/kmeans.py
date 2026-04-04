import numpy as np
from typing import List, Tuple, Dict
import math

# 地球半径 (km)
R = 6371.0

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    计算地球表面两点间的距离（公里）
    使用 Haversine 公式
    """
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c

def haversine_vectorized(lat1_arr, lon1_arr, lat2_arr, lon2_arr):
    """
    向量化的 Haversine 距离计算 (用于 NumPy 数组)
    """
    phi1, phi2 = np.radians(lat1_arr), np.radians(lat2_arr)
    dphi = np.radians(lat2_arr - lat1_arr)
    dlambda = np.radians(lon2_arr - lon1_arr)

    a = np.sin(dphi/2)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    return R * c

def initialize_centroids_around_depot(depot: Tuple[float, float], k: int, radius: float = 5.0) -> np.ndarray:
    """
    在配送站周围初始化聚类中心
    
    Args:
        depot: (lat, lon) 配送站坐标
        k: 聚类数量
        radius: 初始分散半径 (km)
    """
    depot_lat, depot_lon = depot
    
    # 简单的随机初始化：在配送站周围生成随机角度和距离的点
    # 近似计算：1度纬度约111km，1度经度约111*cos(lat)
    
    centroids = []
    for _ in range(k):
        angle = np.random.uniform(0, 2 * np.pi)
        r = np.random.uniform(0, radius)
        
        # 将 km 转换为度数偏移 (近似)
        d_lat = (r / 111.0) * np.cos(angle)
        d_lon = (r / (111.0 * np.cos(np.radians(depot_lat)))) * np.sin(angle)
        
        centroids.append([depot_lat + d_lat, depot_lon + d_lon])
        
    return np.array(centroids)

def assign_points_to_clusters(points: np.ndarray, centroids: np.ndarray) -> np.ndarray:
    """
    将每个点分配给最近的聚类中心
    
    Returns:
        labels: 形状为 (N,) 的数组，表示每个点所属的聚类索引
    """
    N = points.shape[0]
    K = centroids.shape[0]
    
    # 扩展维度以进行广播计算
    # points: (N, 1, 2)
    # centroids: (1, K, 2)
    points_exp = points[:, np.newaxis, :]
    centroids_exp = centroids[np.newaxis, :, :]
    
    # 计算距离矩阵 (N, K)
    # 这一步用欧氏距离做近似分配通常足够快且收敛好，
    # 但为了严谨性，特别是大范围配送，应该用 Haversine。
    # 这里为了性能先用向量化 Haversine。
    
    dists = haversine_vectorized(
        points_exp[:, :, 0], points_exp[:, :, 1],
        centroids_exp[:, :, 0], centroids_exp[:, :, 1]
    )
    
    return np.argmin(dists, axis=1)

def update_centroids_with_constraint(
    points: np.ndarray, 
    labels: np.ndarray, 
    k: int, 
    depot: Tuple[float, float], 
    max_dist: float
) -> np.ndarray:
    """
    更新聚类中心，并应用与配送站的最大距离约束
    """
    new_centroids = []
    depot_lat, depot_lon = depot
    
    for i in range(k):
        # 获取属于该聚类的所有点
        cluster_points = points[labels == i]
        
        if len(cluster_points) == 0:
            # 如果聚类为空，重置到配送站附近（避免死聚类）
            # 或者保持原位？重置通常更好。
            # 这里简单起见，重置为配送站坐标
            new_centroids.append([depot_lat, depot_lon])
            continue
            
        # 计算几何中心 (简单的平均值)
        # 对于经纬度，小范围内平均值是可接受的近似
        centroid_lat = np.mean(cluster_points[:, 0])
        centroid_lon = np.mean(cluster_points[:, 1])
        
        # 检查约束
        dist_to_depot = haversine_distance(depot_lat, depot_lon, centroid_lat, centroid_lon)
        
        if dist_to_depot > max_dist:
            # 如果超出距离，将其拉回到边界上
            # 向量 (depot -> centroid)
            # 新位置 = depot + (vector / dist) * max_dist
            # 需要处理经纬度的方向计算，这里简化处理：
            # 假设地球局部平坦，按比例缩放差值
            
            ratio = max_dist / dist_to_depot
            new_lat = depot_lat + (centroid_lat - depot_lat) * ratio
            new_lon = depot_lon + (centroid_lon - depot_lon) * ratio
            
            new_centroids.append([new_lat, new_lon])
        else:
            new_centroids.append([centroid_lat, centroid_lon])
            
    return np.array(new_centroids)

class ConstrainedKMeans:
    def __init__(self, k: int, max_iterations: int = 100, tolerance: float = 1e-4, max_distance_from_depot: float = 50.0):
        self.k = k
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        self.max_distance_from_depot = max_distance_from_depot
        self.centroids = None
        self.labels = None
        self.inertia = 0.0

    def fit(self, recipients: List[Tuple[float, float]], depot: Tuple[float, float], weights: List[float] = None, courier_capacities: List[float] = None):
        """
        执行约束 K-Means 聚类 (带容量约束)
        
        Args:
            recipients: List of (lat, lon) tuples
            depot: (lat, lon) tuple
            weights: List of weights for each recipient (optional)
            courier_capacities: List of capacity for each courier/cluster (optional)
        """
        points = np.array(recipients)
        n_points = len(points)
        
        # 默认权重为1，默认容量无穷大
        if weights is None:
            weights = np.ones(n_points)
        if courier_capacities is None:
            courier_capacities = [float('inf')] * self.k
            
        # 1. 初始化聚类中心
        self.centroids = initialize_centroids_around_depot(depot, self.k)
        
        for iteration in range(self.max_iterations):
            prev_centroids = self.centroids.copy()
            
            # 2. 分配点到聚类 (带容量约束)
            self.labels = self._assign_points_capacitated(points, self.centroids, weights, courier_capacities)
            
            # 3. 更新聚类中心（带约束）
            self.centroids = update_centroids_with_constraint(
                points, self.labels, self.k, depot, self.max_distance_from_depot
            )
            
            # 4. 检查收敛
            shift = np.linalg.norm(self.centroids - prev_centroids)
            if shift < self.tolerance:
                break
        
        # 计算 Inertia
        self._calculate_inertia(points)
        return self

    def _assign_points_capacitated(self, points: np.ndarray, centroids: np.ndarray, weights: List[float], capacities: List[float]) -> np.ndarray:
        """
        带容量约束的分配算法
        使用贪婪策略：优先分配距离近的点，若满载则找次优
        """
        n_points = points.shape[0]
        k = centroids.shape[0]
        
        # 计算所有点到所有中心的距离 (N, K)
        # points: (N, 2), centroids: (K, 2)
        # 扩展维度进行广播
        points_exp = points[:, np.newaxis, :]
        centroids_exp = centroids[np.newaxis, :, :]
        
        dists = haversine_vectorized(
            points_exp[:, :, 0], points_exp[:, :, 1],
            centroids_exp[:, :, 0], centroids_exp[:, :, 1]
        )
        
        # 记录每个点到每个中心的信息：(distance, point_idx, cluster_idx)
        # 但这样排序比较慢 (N*K)。
        # 优化策略：
        # 对每个点，按距离排序其偏好的 cluster
        
        # 1. 获取每个点对所有聚类的距离排序索引 (N, K)
        sorted_indices = np.argsort(dists, axis=1)
        
        labels = np.full(n_points, -1, dtype=int)
        current_loads = np.zeros(k)
        
        # 2. 决定分配顺序
        # 策略A：按 "遗憾值" (regret) 排序？(次优距离 - 最优距离) 越大越需要优先满足
        # 策略B：简单随机顺序 (避免死锁)
        # 策略C：按在此聚类中的距离排序 (最近的优先得) -> 这会导致远点被踢皮球
        
        # 采用策略A (Regret-based)
        regrets = np.zeros(n_points)
        for i in range(n_points):
            if k > 1:
                regrets[i] = dists[i, sorted_indices[i, 1]] - dists[i, sorted_indices[i, 0]]
            else:
                regrets[i] = 0
                
        # 按遗憾值降序排列，优先处理 "如果不给它最优，它会损失很大" 的点
        priority_order = np.argsort(regrets)[::-1]
        
        for point_idx in priority_order:
            point_weight = weights[point_idx]
            assigned = False
            
            # 尝试分配给首选、次选、...
            for rank in range(k):
                cluster_idx = sorted_indices[point_idx, rank]
                
                if current_loads[cluster_idx] + point_weight <= capacities[cluster_idx]:
                    labels[point_idx] = cluster_idx
                    current_loads[cluster_idx] += point_weight
                    assigned = True
                    break
            
            if not assigned:
                # Fallback Strategy:
                # 1. Try to find ANY cluster that has space, even if distance is far.
                #    Sort clusters by distance to minimize impact, but check ALL.
                for rank in range(k):
                    cluster_idx = sorted_indices[point_idx, rank]
                    if current_loads[cluster_idx] + point_weight <= capacities[cluster_idx]:
                        labels[point_idx] = cluster_idx
                        current_loads[cluster_idx] += point_weight
                        assigned = True
                        break
                
                # 2. If STILL not assigned (Total Capacity < Total Weight, or fragmentation),
                #    Assign to the cluster with the MOST remaining capacity (to minimize overflow).
                if not assigned:
                     # Calculate remaing capacity for all clusters
                     remaining = [capacities[i] - current_loads[i] for i in range(k)]
                     # Find index of max remaining (even if negative)
                     best_fallback = np.argmax(remaining)
                     
                     labels[point_idx] = best_fallback
                     current_loads[best_fallback] += point_weight
                     # This technically violates the hard constraint, but it's the best we can do if P vs NP is hard.
                     # With our new data generation ensuring Total Cap > Total Weight * 1.2, this branch should rarely be hit.
                
        return labels

    def _calculate_inertia(self, points: np.ndarray):
        """计算 Inertia"""
        self.inertia = 0.0
        for i in range(self.k):
            cluster_points = points[self.labels == i]
            if len(cluster_points) > 0:
                c_lat, c_lon = self.centroids[i]
                dists = haversine_vectorized(
                    cluster_points[:, 0], cluster_points[:, 1],
                    np.full(len(cluster_points), c_lat), np.full(len(cluster_points), c_lon)
                )
                self.inertia += np.sum(dists)

    def predict(self, recipients: List[Tuple[float, float]]) -> np.ndarray:
        """预测新点的聚类归属 (不考虑容量)"""
        points = np.array(recipients)
        return assign_points_to_clusters(points, self.centroids)
    
    def get_clusters(self, recipients: List[Tuple[float, float]]) -> Dict[int, List[int]]:
        """
        获取易于使用的聚类结果
        Returns:
            Dict: {cluster_id: [recipient_index_1, recipient_index_2, ...]}
        """
        clusters = {i: [] for i in range(self.k)}
        for idx, label in enumerate(self.labels):
            clusters[label].append(idx)
        return clusters
