<template>
  <div class="history">
    <div class="glass-card header">
      <h2>📊 调度效果分析与对比</h2>
      <div class="header-actions">
        <el-button @click="loadPlans">🔄 刷新</el-button>
        <el-button type="primary" @click="compareMode = !compareMode">
          {{ compareMode ? '退出对比模式' : '📈 多方案对比' }}
        </el-button>
      </div>
    </div>

    <div v-if="!compareMode" class="single-view">
      <div class="stats-overview glass-card">
        <h3>📈 历史调度趋势</h3>
        <div ref="trendChartRef" style="height: 300px"></div>
      </div>

      <div class="plans-grid">
        <div v-for="plan in plans" :key="plan.id" class="plan-card glass-card" @click="selectPlan(plan)">
          <div class="plan-header">
            <h4>{{ plan.title }}</h4>
            <el-tag :type="plan.status === 'READY' ? 'success' : 'info'" size="small">{{ plan.status }}</el-tag>
          </div>
          <div class="plan-time">{{ formatDate(plan.created_at) }}</div>
          <div class="plan-metrics">
            <div class="mini-metric">
              <span class="label">包裹数</span>
              <span class="value">{{ calculateTotalPackages(plan.routes) }}</span>
            </div>
            <div class="mini-metric">
              <span class="label">路线数</span>
              <span class="value">{{ plan.routes?.length || 0 }}</span>
            </div>
            <div class="mini-metric">
              <span class="label">总距离</span>
              <span class="value">{{ calculateTotalDistance(plan.routes) }}km</span>
            </div>
            <div class="mini-metric">
              <span class="label">平均距离</span>
              <span class="value">{{ calculateAvgDistance(plan.routes) }}km</span>
            </div>
          </div>
          <div class="plan-params">
            <el-tag size="small">K={{ plan.algorithm_meta?.k || 'N/A' }}</el-tag>
            <el-tag size="small">代数={{ plan.algorithm_meta?.generations || 'N/A' }}</el-tag>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="compare-view">
      <div class="compare-selector glass-card">
        <h3>选择对比方案（最多3个）</h3>
        <el-checkbox-group v-model="selectedPlans" :max="3">
          <el-checkbox v-for="plan in plans" :key="plan.id" :label="plan.id" :disabled="selectedPlans.length >= 3 && !selectedPlans.includes(plan.id)">
            {{ plan.title }} - {{ formatDate(plan.created_at) }}
          </el-checkbox>
        </el-checkbox-group>
      </div>

      <div v-if="selectedPlans.length >= 2" class="compare-content">
        <div class="compare-chart glass-card">
          <h3>📊 方案对比分析</h3>
          <div ref="compareChartRef" style="height: 350px"></div>
        </div>

        <div class="compare-table glass-card">
          <h3>📋 详细对比</h3>
          <el-table :data="comparisonData" style="margin-top: 12px">
            <el-table-column label="指标" prop="metric" width="150" fixed />
            <el-table-column v-for="(planId, idx) in selectedPlans" :key="planId" :label="`方案${idx + 1}`">
              <template #default="{ row }">
                <span :class="{ best: row.bestIndex === idx }">{{ row.values[idx] }}</span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'

const plans = ref<any[]>([])
const compareMode = ref(false)
const selectedPlans = ref<number[]>([])
const trendChartRef = ref()
const compareChartRef = ref()

const loadPlans = async () => {
  try {
    const res = await axios.get('/api/v1/dispatch/plans')
    plans.value = res.data.filter((p: any) => (p.status === 'READY' || p.status === 'COMPLETED') && p.routes?.length > 0)
    if (plans.value.length > 0) {
      initTrendChart()
    }
  } catch (e) {
    console.error(e)
  }
}

onMounted(() => loadPlans())

watch(selectedPlans, () => {
  if (selectedPlans.value.length >= 2) {
    setTimeout(() => initCompareChart(), 100)
  }
})

const initTrendChart = () => {
  if (!trendChartRef.value) return
  const chart = echarts.init(trendChartRef.value)

  const dates = plans.value.map(p => formatDate(p.created_at).split(' ')[0])
  const distances = plans.value.map(p => parseFloat(calculateTotalDistance(p.routes)))
  const avgDistances = plans.value.map(p => parseFloat(calculateAvgDistance(p.routes)))
  const packages = plans.value.map(p => calculateTotalPackages(p.routes))

  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['总距离', '平均距离', '包裹数'], top: 0 },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '15%', containLabel: true },
    xAxis: { type: 'category', data: dates },
    yAxis: [
      { type: 'value', name: '距离(km)' },
      { type: 'value', name: '包裹数' }
    ],
    series: [
      { name: '总距离', type: 'line', data: distances, smooth: true, itemStyle: { color: '#667eea' } },
      { name: '平均距离', type: 'line', data: avgDistances, smooth: true, itemStyle: { color: '#48bb78' } },
      { name: '包裹数', type: 'bar', yAxisIndex: 1, data: packages, itemStyle: { color: '#ed8936' } }
    ]
  })
}

const initCompareChart = () => {
  if (!compareChartRef.value) return
  const chart = echarts.init(compareChartRef.value)

  const selectedPlanData = selectedPlans.value.map(id => plans.value.find(p => p.id === id))
  const labels = selectedPlanData.map((_, idx) => `方案${idx + 1}`)

  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['总距离', '包裹数', '路线数', '平均距离'] },
    radar: {
      indicator: [
        { name: '总距离(km)', max: Math.max(...selectedPlanData.map(p => parseFloat(calculateTotalDistance(p.routes)))) * 1.2 },
        { name: '包裹数', max: Math.max(...selectedPlanData.map(p => calculateTotalPackages(p.routes))) * 1.2 },
        { name: '路线数', max: Math.max(...selectedPlanData.map(p => p.routes?.length || 0)) * 1.2 },
        { name: '平均距离(km)', max: Math.max(...selectedPlanData.map(p => parseFloat(calculateAvgDistance(p.routes)))) * 1.2 }
      ]
    },
    series: [{
      type: 'radar',
      data: selectedPlanData.map((plan, idx) => ({
        value: [
          parseFloat(calculateTotalDistance(plan.routes)),
          calculateTotalPackages(plan.routes),
          plan.routes?.length || 0,
          parseFloat(calculateAvgDistance(plan.routes))
        ],
        name: labels[idx]
      }))
    }]
  })
}

const comparisonData = computed(() => {
  if (selectedPlans.value.length < 2) return []

  const selectedPlanData = selectedPlans.value.map(id => plans.value.find(p => p.id === id))

  const metrics = [
    { metric: '总包裹数', values: selectedPlanData.map(p => calculateTotalPackages(p.routes)), lower: false },
    { metric: '路线数', values: selectedPlanData.map(p => p.routes?.length || 0), lower: false },
    { metric: '总距离(km)', values: selectedPlanData.map(p => calculateTotalDistance(p.routes)), lower: true },
    { metric: '平均距离(km)', values: selectedPlanData.map(p => calculateAvgDistance(p.routes)), lower: true },
    { metric: 'K值', values: selectedPlanData.map(p => p.algorithm_meta?.k || 'N/A'), lower: false },
    { metric: '遗传代数', values: selectedPlanData.map(p => p.algorithm_meta?.generations || 'N/A'), lower: false }
  ]

  return metrics.map(m => {
    const numericValues = m.values.filter(v => typeof v === 'number')
    const bestIndex = numericValues.length > 0
      ? m.values.indexOf(m.lower ? Math.min(...numericValues) : Math.max(...numericValues))
      : -1
    return { ...m, bestIndex }
  })
})

const selectPlan = (plan: any) => {
  console.log('Selected plan:', plan)
}

const formatDate = (date: string) => new Date(date).toLocaleString('zh-CN')
const calculateTotalDistance = (routes: any[]) => routes?.reduce((sum, r) => sum + (r.geo_json?.total_distance_km || 0), 0).toFixed(1) || '0.0'
const calculateTotalPackages = (routes: any[]) => routes?.reduce((sum, r) => sum + (r.geo_json?.package_count || 0), 0) || 0
const calculateAvgDistance = (routes: any[]) => {
  const total = parseFloat(calculateTotalDistance(routes))
  const packages = calculateTotalPackages(routes)
  return packages > 0 ? (total / packages).toFixed(2) : '0.00'
}
</script>

<style scoped>
.history { display: flex; flex-direction: column; gap: 20px; }
.glass-card { background: rgba(255,255,255,0.9); backdrop-filter: blur(20px); border-radius: 16px; padding: 24px; box-shadow: 0 8px 32px rgba(0,0,0,0.1); }
h2, h3, h4 { margin: 0; }

.header { display: flex; justify-content: space-between; align-items: center; }
.header-actions { display: flex; gap: 12px; }

.single-view { display: flex; flex-direction: column; gap: 20px; }
.stats-overview { margin-bottom: 8px; }

.plans-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px; }
.plan-card { cursor: pointer; transition: all 0.3s; }
.plan-card:hover { transform: translateY(-4px); box-shadow: 0 12px 40px rgba(102, 126, 234, 0.2); }

.plan-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.plan-time { font-size: 13px; color: #718096; margin-bottom: 12px; }

.plan-metrics { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-bottom: 12px; }
.mini-metric { display: flex; flex-direction: column; padding: 8px; background: rgba(102, 126, 234, 0.05); border-radius: 6px; }
.mini-metric .label { font-size: 12px; color: #718096; margin-bottom: 4px; }
.mini-metric .value { font-size: 18px; font-weight: bold; color: #667eea; }

.plan-params { display: flex; gap: 8px; }

.compare-view { display: flex; flex-direction: column; gap: 20px; }
.compare-selector { margin-bottom: 8px; }
.compare-selector h3 { margin-bottom: 16px; }
.el-checkbox-group { display: flex; flex-direction: column; gap: 12px; }

.compare-content { display: flex; flex-direction: column; gap: 20px; }
.compare-chart, .compare-table { margin-top: 0; }

.best { color: #48bb78; font-weight: bold; }
</style>
