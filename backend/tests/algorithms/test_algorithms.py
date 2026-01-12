import pytest
import numpy as np
from app.core.algorithms.kmeans import haversine_distance, ConstrainedKMeans
from app.core.algorithms.genetic import GeneticAlgorithmTSP

# -----------------------------------------------------------------------------
# 测试数据准备
# -----------------------------------------------------------------------------

# 配送站 (北京天安门附近)
DEPOT = (39.9087, 116.3975)

# 模拟两组聚类点
# 组1：东单附近 (东边)
GROUP1 = [
    (39.9080, 116.4100),
    (39.9090, 116.4110),
    (39.9070, 116.4120),
]
# 组2：西单附近 (西边)
GROUP2 = [
    (39.9080, 116.3700),
    (39.9090, 116.3710),
    (39.9070, 116.3720),
]

ALL_POINTS = GROUP1 + GROUP2

# -----------------------------------------------------------------------------
# 测试用例
# -----------------------------------------------------------------------------

def test_haversine_distance():
    """测试距离计算准确性"""
    # 北京到上海的大致距离 (直线)
    # 北京 (39.9042, 116.4074)
    # 上海 (31.2304, 121.4737)
    # 距离约 1068 km
    
    d = haversine_distance(39.9042, 116.4074, 31.2304, 121.4737)
    assert 1000 < d < 1200, f"Distance {d} seems wrong for Beijing-Shanghai"
    
    # 同一点距离应为0
    assert haversine_distance(39.9, 116.4, 39.9, 116.4) == 0

def test_kmeans_clustering_basic():
    """测试 K-Means 基本聚类功能"""
    # 期望将东单和西单分为2类
    kmeans = ConstrainedKMeans(k=2, max_iterations=50)
    kmeans.fit(ALL_POINTS, DEPOT)
    
    clusters = kmeans.get_clusters(ALL_POINTS)
    
    # 验证是否产生了2个聚类
    assert len(clusters) == 2
    
    # 验证每个聚类都不为空 (在这个简单例子中应该如此)
    # 注意：K-Means 随机初始化可能导致不同结果，但在这种分离明显的例子中通常很稳定
    assert len(clusters[0]) > 0
    assert len(clusters[1]) > 0
    
    # 验证总点数
    total_points = sum(len(c) for c in clusters.values())
    assert total_points == 6

def test_kmeans_constraint():
    """测试 K-Means 的距离约束"""
    # 设定一个极小的最大距离约束 (例如 0.5km)
    # 只有离配送站非常近的点才能成为中心，或者中心被强制拉回
    
    # 注意：我们的约束逻辑是 "拉回中心"，而不是 "丢弃点"
    # 所以测试重点是检查 centroids 是否都在范围内
    
    max_dist = 0.5 # km
    kmeans = ConstrainedKMeans(k=2, max_distance_from_depot=max_dist)
    kmeans.fit(ALL_POINTS, DEPOT)
    
    for centroid in kmeans.centroids:
        dist = haversine_distance(DEPOT[0], DEPOT[1], centroid[0], centroid[1])
        # 允许微小误差
        assert dist <= max_dist + 0.01, f"Centroid {centroid} is too far from depot ({dist} km)"

def test_genetic_algorithm_tsp():
    """测试遗传算法 TSP"""
    # 使用 GROUP1 的3个点 + 配送站
    # 总共3个配送点
    
    ga = GeneticAlgorithmTSP(
        population_size=20,
        generations=50,
        crossover_rate=0.8,
        mutation_rate=0.1
    )
    
    best_route, fitness_history = ga.solve(GROUP1, DEPOT)
    
    # 验证输出格式
    assert isinstance(best_route, list)
    assert len(best_route) == len(GROUP1)
    
    # 验证包含了所有点的索引 (0, 1, 2)
    assert sorted(best_route) == [0, 1, 2]
    
    # 验证适应度进化 (通常最后一代适应度 >= 第一代)
    assert fitness_history[-1] >= fitness_history[0]

def test_genetic_algorithm_empty():
    """测试空输入情况"""
    ga = GeneticAlgorithmTSP()
    route, _ = ga.solve([], DEPOT)
    assert route == []

def test_genetic_algorithm_single_point():
    """测试单点情况"""
    ga = GeneticAlgorithmTSP()
    route, _ = ga.solve([(39.9, 116.4)], DEPOT)
    assert route == [0]
