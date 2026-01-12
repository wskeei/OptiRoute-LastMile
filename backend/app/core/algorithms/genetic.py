import random
import numpy as np
from typing import List, Tuple, Dict, Optional
from .kmeans import haversine_distance

class GeneticAlgorithmTSP:
    def __init__(
        self,
        population_size: int = 100,
        generations: int = 500,
        crossover_rate: float = 0.8,
        mutation_rate: float = 0.1,
        elite_ratio: float = 0.1,
        tournament_size: int = 3
    ):
        self.population_size = population_size
        self.generations = generations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.elite_count = int(elite_ratio * population_size)
        self.tournament_size = tournament_size
        
    def solve(self, addresses: List[Tuple[float, float]], depot: Tuple[float, float], progress_callback=None) -> Tuple[List[int], List[float]]:
        """
        遗传算法求解 TSP
        
        Args:
            addresses: 收件地址坐标列表 [(lat, lon), ...]
            depot: 配送站坐标 (lat, lon)
            progress_callback: Optional callable that receives (generation, best_route_indices, best_fitness)
            
        Returns:
            best_route: 最优路径的索引顺序 [idx1, idx2, ..., idxN]
            fitness_history: 每一代的最佳适应度历史
        """
        num_cities = len(addresses)
        if num_cities == 0:
            return [], []
        if num_cities == 1:
            return [0], []

        # 1. 初始化种群
        population = self._initialize_population(num_cities)
        
        best_fitness_history = []
        best_chromosome = None
        best_fitness = -1.0
        
        # 自适应变异参数
        current_mutation_rate = self.mutation_rate
        stagnation_counter = 0
        
        for generation in range(self.generations):
            # 2. 计算适应度
            fitnesses = [self._fitness(chromo, addresses, depot) for chromo in population]
            
            # 3. 记录最优解
            current_best_idx = np.argmax(fitnesses)
            current_best_fitness = fitnesses[current_best_idx]
            current_best_chromo = population[current_best_idx]

            # 3.1 局部搜索 (2-Opt) 优化当前最优解
            # 仅对精英个体执行，避免性能开销过大
            improved_chromo = self._two_opt_search(current_best_chromo, addresses, depot)
            improved_fitness = self._fitness(improved_chromo, addresses, depot)
            
            if improved_fitness > current_best_fitness:
                current_best_fitness = improved_fitness
                current_best_chromo = improved_chromo
                # 更新种群中的最优个体
                population[current_best_idx] = improved_chromo
                fitnesses[current_best_idx] = improved_fitness

            # 更新全局最优
            if current_best_fitness > best_fitness:
                best_fitness = current_best_fitness
                best_chromosome = current_best_chromo[:]
                stagnation_counter = 0
                # 如果找到更好解，恢复基准变异率
                current_mutation_rate = self.mutation_rate
            else:
                stagnation_counter += 1
                
            # 自适应变异：若 20 代无提升，增加变异率
            if stagnation_counter > 20:
                current_mutation_rate = min(0.5, current_mutation_rate * 1.5)
                stagnation_counter = 0 # Reset to let it explore
            
            best_fitness_history.append(current_best_fitness)
            
            if progress_callback and generation % 5 == 0: # Check periodically
                 progress_callback(generation, best_chromosome, current_best_fitness)
            
            # 4. 生成下一代
            new_population = []
            
            # 4.1 精英保留
            elite_indices = np.argsort(fitnesses)[-self.elite_count:]
            for idx in elite_indices:
                new_population.append(population[idx][:])
                
            # 4.2 交叉和变异
            while len(new_population) < self.population_size:
                parent1 = self._tournament_selection(population, fitnesses)
                parent2 = self._tournament_selection(population, fitnesses)
                
                if random.random() < self.crossover_rate:
                    child1 = self._order_crossover(parent1, parent2)
                    child2 = self._order_crossover(parent2, parent1)
                else:
                    child1 = parent1[:]
                    child2 = parent2[:]
                
                # 使用当前自适应变异率
                child1 = self._swap_mutation(child1, current_mutation_rate)
                child2 = self._swap_mutation(child2, current_mutation_rate)
                
                new_population.append(child1)
                if len(new_population) < self.population_size:
                    new_population.append(child2)
            
            population = new_population
            
        return best_chromosome, best_fitness_history

    def _two_opt_search(self, route: List[int], addresses: List[Tuple[float, float]], depot: Tuple[float, float]) -> List[int]:
        """
        2-Opt 局部搜索
        """
        best_route = route[:]
        best_dist = 1.0 / self._fitness(route, addresses, depot) # 反推距离
        
        improved = True
        max_iterations = 50 # 限制局部搜索次数，防止耗时过长
        count = 0
        
        while improved and count < max_iterations:
            improved = False
            count += 1
            n = len(route)
            
            # 尝试交换所有可能的边 (i, i+1) 和 (j, j+1)
            # 路径: Depot -> r[0] ... r[n-1] -> Depot
            # 2-opt 在线性路径上通常是翻转片段 r[i:j+1]
            
            for i in range(n - 1):
                for j in range(i + 1, n):
                    # 翻转 i 到 j 的片段
                    new_route = best_route[:]
                    new_route[i:j+1] = best_route[i:j+1][::-1]
                    
                    dist = 1.0 / self._fitness(new_route, addresses, depot)
                    
                    if dist < best_dist - 1e-6:
                        best_dist = dist
                        best_route = new_route
                        improved = True
                        break # First improvement 策略
                if improved: break
                
        return best_route

    def _initialize_population(self, num_cities: int) -> List[List[int]]:
        """初始化随机种群"""
        population = []
        base_indices = list(range(num_cities))
        for _ in range(self.population_size):
            # 随机打乱生成一个染色体
            chromosome = base_indices[:]
            random.shuffle(chromosome)
            population.append(chromosome)
        return population

    def _fitness(self, chromosome: List[int], addresses: List[Tuple[float, float]], depot: Tuple[float, float]) -> float:
        """
        计算适应度 = 1 / (总路径距离 + epsilon)
        路径: Depot -> Addr[chromo[0]] -> ... -> Addr[chromo[-1]] -> Depot
        """
        total_dist = 0.0
        current_pos = depot
        
        for idx in chromosome:
            next_pos = addresses[idx]
            total_dist += haversine_distance(current_pos[0], current_pos[1], next_pos[0], next_pos[1])
            current_pos = next_pos
            
        # 回到配送站
        total_dist += haversine_distance(current_pos[0], current_pos[1], depot[0], depot[1])
        
        return 1.0 / (total_dist + 1e-6)

    def _tournament_selection(self, population: List[List[int]], fitnesses: List[float]) -> List[int]:
        """锦标赛选择"""
        # 随机选择 tournament_size 个个体的索引
        indices = random.sample(range(len(population)), self.tournament_size)
        
        # 找到其中适应度最高的
        best_idx = indices[0]
        best_val = fitnesses[best_idx]
        
        for idx in indices[1:]:
            if fitnesses[idx] > best_val:
                best_val = fitnesses[idx]
                best_idx = idx
                
        return population[best_idx]

    def _order_crossover(self, parent1: List[int], parent2: List[int]) -> List[int]:
        """
        顺序交叉 (OX1)
        保留 parent1 的一段子序列，剩余部分按 parent2 的顺序填充
        """
        size = len(parent1)
        
        # Handle case where size < 2
        if size < 2: return parent1[:]

        start, end = sorted(random.sample(range(size), 2))
        
        child = [-1] * size
        # 复制 parent1 的片段
        child[start:end] = parent1[start:end]
        
        # 构建 parent2 的旋转列表 (从 end 开始)
        p2_rotated = parent2[end:] + parent2[:end]
        
        current_idx = end
        for gene in p2_rotated:
            if gene not in child: 
                if current_idx >= size:
                    current_idx = 0
                
                # 找到下一个空位
                while child[current_idx] != -1:
                    current_idx = (current_idx + 1) % size
                
                child[current_idx] = gene
                
        return child

    def _swap_mutation(self, chromosome: List[int], mutation_rate: float) -> List[int]:
        """交换变异"""
        if random.random() < mutation_rate and len(chromosome) > 1:
            idx1, idx2 = random.sample(range(len(chromosome)), 2)
            chromosome[idx1], chromosome[idx2] = chromosome[idx2], chromosome[idx1]
        return chromosome
