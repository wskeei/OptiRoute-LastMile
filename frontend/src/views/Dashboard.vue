<template>
  <div class="dashboard">
    <div class="hero-section glass-card">
      <h1>🚀 AI智能配送调度系统</h1>
      <p class="subtitle">基于K-Means聚类与遗传算法的末端配送路径优化解决方案</p>
    </div>

    <div class="features-grid">
      <div class="feature-card glass-card" @click="$router.push('/dispatch')">
        <div class="feature-icon">🤖</div>
        <h3>AI智能调度</h3>
        <p>一键生成最优配送路线</p>
      </div>
      <div class="feature-card glass-card" @click="$router.push('/analytics')">
        <div class="feature-icon">📊</div>
        <h3>数据分析中心</h3>
        <p>全面的配送数据分析</p>
      </div>
      <div class="feature-card glass-card" @click="$router.push('/monitor')">
        <div class="feature-icon">🗺️</div>
        <h3>实时监控</h3>
        <p>可视化配送过程模拟</p>
      </div>
      <div class="feature-card glass-card" @click="$router.push('/history')">
        <div class="feature-icon">📈</div>
        <h3>效果对比</h3>
        <p>多方案对比分析</p>
      </div>
    </div>

    <div class="stats-row">
      <div class="stat-card glass-card">
        <div class="stat-number">{{ stats.totalPackages }}</div>
        <div class="stat-label">总包裹数</div>
      </div>
      <div class="stat-card glass-card">
        <div class="stat-number">{{ stats.totalCouriers }}</div>
        <div class="stat-label">快递员数</div>
      </div>
      <div class="stat-card glass-card">
        <div class="stat-number">{{ stats.totalPlans }}</div>
        <div class="stat-label">调度次数</div>
      </div>
      <div class="stat-card glass-card">
        <div class="stat-number">{{ stats.savedDistance }}</div>
        <div class="stat-label">优化距离(km)</div>
      </div>
    </div>

    <div class="chart-section glass-card">
      <h3>📈 最近调度趋势</h3>
      <div ref="chartRef" style="height: 280px"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'

const stats = ref({ totalPackages: 0, totalCouriers: 0, totalPlans: 0, savedDistance: 0 })
const chartRef = ref()

onMounted(async () => {
  try {
    const [packagesRes, couriersRes, plansRes] = await Promise.all([
      axios.get('/api/v1/delivery/packages'),
      axios.get('/api/v1/delivery/couriers'),
      axios.get('/api/v1/dispatch/plans')
    ])

    stats.value.totalPackages = packagesRes.data.length
    stats.value.totalCouriers = couriersRes.data.length

    const completedPlans = plansRes.data.filter((p: any) => (p.status === 'READY' || p.status === 'COMPLETED') && p.routes?.length > 0)
    stats.value.totalPlans = completedPlans.length

    const totalDistance = completedPlans.reduce((sum: number, p: any) =>
      sum + (p.routes?.reduce((s: number, r: any) => s + (r.geo_json?.total_distance_km || 0), 0) || 0), 0)
    stats.value.savedDistance = totalDistance.toFixed(1)

    if (chartRef.value && completedPlans.length > 0) {
      const chart = echarts.init(chartRef.value)
      const recentPlans = completedPlans.slice(-8)
      const dates = recentPlans.map((_: any, i: number) => `第${i + 1}次`)
      const distances = recentPlans.map((p: any) =>
        p.routes?.reduce((s: number, r: any) => s + (r.geo_json?.total_distance_km || 0), 0) || 0
      )
      const packages = recentPlans.map((p: any) =>
        p.routes?.reduce((s: number, r: any) => s + (r.geo_json?.package_count || 0), 0) || 0
      )

      chart.setOption({
        tooltip: { trigger: 'axis' },
        legend: { data: ['总距离', '包裹数'], top: 0 },
        grid: { left: '3%', right: '4%', bottom: '3%', top: '15%', containLabel: true },
        xAxis: { type: 'category', data: dates },
        yAxis: [
          { type: 'value', name: '距离(km)' },
          { type: 'value', name: '包裹数' }
        ],
        series: [
          { name: '总距离', type: 'line', data: distances, smooth: true, itemStyle: { color: '#667eea' } },
          { name: '包裹数', type: 'bar', yAxisIndex: 1, data: packages, itemStyle: { color: '#48bb78' } }
        ]
      })
    }
  } catch (e) {
    console.error(e)
  }
})
</script>

<style scoped>
.dashboard { display: flex; flex-direction: column; gap: 24px; }
.glass-card { background: rgba(255,255,255,0.9); backdrop-filter: blur(20px); border-radius: 16px; padding: 24px; box-shadow: 0 8px 32px rgba(0,0,0,0.1); }

.hero-section { text-align: center; padding: 40px 24px; }
.hero-section h1 { margin: 0 0 12px 0; font-size: 36px; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.subtitle { margin: 0; font-size: 16px; color: #718096; }

.features-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }
.feature-card { text-align: center; padding: 32px 24px; cursor: pointer; transition: all 0.3s; }
.feature-card:hover { transform: translateY(-8px); box-shadow: 0 16px 48px rgba(102, 126, 234, 0.2); }
.feature-icon { font-size: 48px; margin-bottom: 16px; }
.feature-card h3 { margin: 0 0 8px 0; font-size: 18px; color: #2d3748; }
.feature-card p { margin: 0; font-size: 14px; color: #718096; }

.stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }
.stat-card { text-align: center; padding: 24px; }
.stat-number { font-size: 36px; font-weight: bold; color: #667eea; margin-bottom: 8px; }
.stat-label { font-size: 14px; color: #718096; }

.chart-section h3 { margin: 0 0 16px 0; }
</style>
