<template>
  <div class="history">
    <div class="glass-card header">
      <div class="header-text">
        <h2>历史调度记录与复盘</h2>
        <p class="header-note">
          按时间线回看已完成的调度方案，选取任何一条记录即可展开复盘细节。
        </p>
      </div>
      <div class="header-actions">
        <el-button @click="loadPlans">刷新记录</el-button>
        <el-button type="primary" @click="compareMode = !compareMode">
          {{ compareMode ? '退出复盘对比' : '进入复盘对比' }}
        </el-button>
      </div>
    </div>

    <div v-if="!loading && !loadError && plans.length === 0" class="glass-card empty-history">
      <h3>还没有已完成的调度记录</h3>
      <p>先前往调度中心重置演示数据并发起一次调度，完成后这里会出现可复盘的路线记录。</p>
      <router-link class="empty-link" :to="ONBOARDING_STEPS[0]?.path || '/dispatch'">
        {{ ONBOARDING_STEPS[0]?.actionLabel || '前往调度中心' }}
      </router-link>
    </div>

    <div v-else-if="loading" class="glass-card empty-history">
      <h3>正在加载历史记录</h3>
      <p>请稍候，系统正在读取已完成的调度计划。</p>
    </div>

    <div v-else-if="loadError" class="glass-card empty-history">
      <h3>历史记录加载失败</h3>
      <p>{{ loadError }}</p>
      <router-link class="empty-link" to="/dispatch">前往调度中心</router-link>
    </div>

    <div v-else-if="!compareMode" class="single-view">
      <div class="stats-overview glass-card">
        <h3>历史调度趋势</h3>
        <p class="section-note">图表按照创建时间顺序展示已完成记录，供复盘走查。</p>
        <div ref="trendChartRef" style="height: 300px"></div>
      </div>

      <div class="history-grid">
        <div v-for="plan in plans" :key="plan.id" class="plan-card glass-card">
          <div class="plan-header">
            <div>
              <h4>{{ plan.title }}</h4>
              <div class="plan-time">{{ formatDate(plan.created_at) }}</div>
            </div>
            <el-tag :type="plan.status === 'READY' ? 'success' : 'info'" size="small">{{ getStatusLabel(plan.status) }}</el-tag>
          </div>
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
            <div class="mini-metric">
              <span class="label">总重量</span>
              <span class="value">{{ calculateTotalWeight(plan.routes) }}kg</span>
            </div>
          </div>
          <div class="plan-params">
            <el-tag size="small">K={{ plan.algorithm_meta?.k || 'N/A' }}</el-tag>
            <el-tag size="small">代数={{ plan.algorithm_meta?.generations || 'N/A' }}</el-tag>
          </div>
          <div class="plan-actions">
            <el-button type="text" @click.stop="openPlanDetail(plan)">查看复盘</el-button>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="compare-view">
      <div class="compare-selector glass-card">
        <h3>选择复盘对比方案（最多3个）</h3>
        <el-checkbox-group v-model="selectedPlans" :max="3">
          <el-checkbox v-for="plan in plans" :key="plan.id" :label="plan.id" :disabled="selectedPlans.length >= 3 && !selectedPlans.includes(plan.id)">
            {{ plan.title }} - {{ formatDate(plan.created_at) }}
          </el-checkbox>
        </el-checkbox-group>
      </div>

      <div v-if="selectedPlans.length >= 2" class="compare-content">
        <div class="compare-chart glass-card">
          <h3>方案复盘对比</h3>
          <div ref="compareChartRef" style="height: 350px"></div>
        </div>

        <div class="compare-table glass-card">
          <h3>详细复盘指标</h3>
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
    <el-drawer
      v-model="detailDrawerVisible"
      title="调度方案复盘"
      direction="rtl"
      :size="drawerSize"
      destroy-on-close
    >
      <div v-if="activePlan">
        <el-descriptions column="1" size="small" class="detail-descriptions">
          <el-descriptions-item label="方案名称">{{ activePlan.title }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(activePlan.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="状态">{{ getStatusLabel(activePlan.status) }}</el-descriptions-item>
          <el-descriptions-item label="总包裹数">{{ calculateTotalPackages(activePlan.routes) }}</el-descriptions-item>
          <el-descriptions-item label="路线数">{{ activePlan.routes?.length || 0 }}</el-descriptions-item>
          <el-descriptions-item label="总距离">{{ calculateTotalDistance(activePlan.routes) }} km</el-descriptions-item>
          <el-descriptions-item label="总重量">{{ calculateTotalWeight(activePlan.routes) }} kg</el-descriptions-item>
        </el-descriptions>
        <el-divider />
        <div class="route-list">
          <h4>路线快照</h4>
          <el-collapse accordion>
            <el-collapse-item
              v-for="(route, idx) in activePlan.routes || []"
              :key="route.id ?? idx"
              :name="idx"
              :title="route.name || `路线${Number(idx) + 1}`"
            >
              <p>包裹数：{{ formatRoutePackageCount(route) }}</p>
              <p>距离：{{ formatRouteDistance(route) }} km</p>
              <p>重量：{{ formatRouteWeight(route) }} kg</p>
            </el-collapse-item>
          </el-collapse>
        </div>
      </div>
      <div v-else class="empty-state">
        请选择历史记录查看复盘详情。
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch, computed } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'
import { ONBOARDING_STEPS } from '../lib/ux'
import { getCompletedPlans } from '../lib/analytics'

const plans = ref<any[]>([])
const compareMode = ref(false)
const selectedPlans = ref<number[]>([])
const trendChartRef = ref()
const compareChartRef = ref()
const detailDrawerVisible = ref(false)
const activePlan = ref<any | null>(null)
const loading = ref(false)
const loadError = ref('')
const drawerSize = ref('460px')

const syncDrawerSize = () => {
  if (typeof window === 'undefined') return
  drawerSize.value = window.innerWidth < 640 ? '100%' : '460px'
}

const loadPlans = async () => {
  loading.value = true
  loadError.value = ''
  try {
    const res = await axios.get('/api/v1/dispatch/plans')
    plans.value = getCompletedPlans(res.data)
    if (plans.value.length > 0) {
      initTrendChart()
    }
  } catch (e) {
    console.error(e)
    loadError.value = '请刷新页面，或先前往调度中心生成第一条调度结果。'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  syncDrawerSize()
  window.addEventListener('resize', syncDrawerSize)
  loadPlans()
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', syncDrawerSize)
})

watch(selectedPlans, () => {
  if (selectedPlans.value.length >= 2) {
    setTimeout(() => initCompareChart(), 100)
  }
})

watch(compareMode, (value) => {
  if (!value) {
    selectedPlans.value = []
  }
})

watch(detailDrawerVisible, (visible) => {
  if (!visible) {
    activePlan.value = null
  }
})

const openPlanDetail = (plan: any) => {
  activePlan.value = plan
  detailDrawerVisible.value = true
}

const initTrendChart = () => {
  if (!trendChartRef.value) return
  const chart = echarts.init(trendChartRef.value)

  const dates = plans.value.map((plan) => formatDate(plan.created_at).split(' ')[0])
  const distances = plans.value.map((plan) => parseFloat(calculateTotalDistance(plan.routes)))
  const avgDistances = plans.value.map((plan) => parseFloat(calculateAvgDistance(plan.routes)))
  const packages = plans.value.map((plan) => calculateTotalPackages(plan.routes))
  const weights = plans.value.map((plan) => parseFloat(calculateTotalWeight(plan.routes)))

  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['总距离', '平均距离', '包裹数', '总重量'], top: 0 },
    grid: { left: '3%', right: '15%', bottom: '3%', top: '15%', containLabel: true },
    xAxis: { type: 'category', data: dates },
    yAxis: [
      { type: 'value', name: '距离(km)', position: 'left' },
      { type: 'value', name: '包裹数', position: 'right' },
      {
        type: 'value',
        name: '重量(kg)',
        position: 'right',
        offset: 50,
        axisLine: { show: true, lineStyle: { color: '#9f7aea' } }
      }
    ],
    series: [
      { name: '总距离', type: 'line', data: distances, smooth: true, itemStyle: { color: '#667eea' } },
      { name: '平均距离', type: 'line', data: avgDistances, smooth: true, itemStyle: { color: '#48bb78' } },
      { name: '包裹数', type: 'bar', yAxisIndex: 1, data: packages, itemStyle: { color: '#ed8936' } },
      { name: '总重量', type: 'line', yAxisIndex: 2, data: weights, smooth: true, itemStyle: { color: '#9f7aea' } }
    ]
  })
}

const initCompareChart = () => {
  if (!compareChartRef.value) return
  const chart = echarts.init(compareChartRef.value)

  const selectedPlanData = selectedPlans.value
    .map((id) => plans.value.find((plan) => plan.id === id))
    .filter((plan): plan is NonNullable<typeof plan> => Boolean(plan))

  if (selectedPlanData.length < 2) return

  const labels = selectedPlanData.map((_, idx) => `方案${idx + 1}`)
  const parseNumber = (value: string) => {
    const num = parseFloat(value)
    return Number.isNaN(num) ? 0 : num
  }
  const distances = selectedPlanData.map((plan) => parseNumber(calculateTotalDistance(plan.routes)))
  const packageCounts = selectedPlanData.map((plan) => calculateTotalPackages(plan.routes))
  const routeCounts = selectedPlanData.map((plan) => plan.routes?.length || 0)
  const avgDistances = selectedPlanData.map((plan) => parseNumber(calculateAvgDistance(plan.routes)))
  const safeMax = (values: number[]) => (values.length ? Math.max(...values) : 0)

  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['总距离', '包裹数', '路线数', '平均距离'] },
    radar: {
      indicator: [
        { name: '总距离(km)', max: safeMax(distances) * 1.2 },
        { name: '包裹数', max: safeMax(packageCounts) * 1.2 },
        { name: '路线数', max: safeMax(routeCounts) * 1.2 },
        { name: '平均距离(km)', max: safeMax(avgDistances) * 1.2 }
      ]
    },
    series: [{
      type: 'radar',
      data: selectedPlanData.map((_, idx) => ({
        value: [distances[idx], packageCounts[idx], routeCounts[idx], avgDistances[idx]],
        name: labels[idx]
      }))
    }]
  })
}

const comparisonData = computed(() => {
  if (selectedPlans.value.length < 2) return []

  const selectedPlanData = selectedPlans.value
    .map((id) => plans.value.find((plan) => plan.id === id))
    .filter((plan): plan is NonNullable<typeof plan> => Boolean(plan))

  if (selectedPlanData.length < 2) return []

  const metrics = [
    { metric: '总包裹数', values: selectedPlanData.map((plan) => calculateTotalPackages(plan.routes)), lower: false },
    { metric: '总重量(kg)', values: selectedPlanData.map((plan) => calculateTotalWeight(plan.routes)), lower: false },
    { metric: '路线数', values: selectedPlanData.map((plan) => plan.routes?.length || 0), lower: false },
    { metric: '总距离(km)', values: selectedPlanData.map((plan) => calculateTotalDistance(plan.routes)), lower: true },
    { metric: '平均距离(km)', values: selectedPlanData.map((plan) => calculateAvgDistance(plan.routes)), lower: true },
    { metric: 'K值', values: selectedPlanData.map((plan) => plan.algorithm_meta?.k || 'N/A'), lower: false },
    { metric: '遗传代数', values: selectedPlanData.map((plan) => plan.algorithm_meta?.generations || 'N/A'), lower: false }
  ]

  return metrics.map((metric) => {
    const numericValues = metric.values.filter((value) => typeof value === 'number')
    const bestIndex = numericValues.length > 0
      ? metric.values.indexOf(metric.lower ? Math.min(...numericValues) : Math.max(...numericValues))
      : -1
    return { ...metric, bestIndex }
  })
})

const formatDate = (date: string) => new Date(date).toLocaleString('zh-CN')
const calculateTotalDistance = (routes: any[]) => routes?.reduce((sum, route) => sum + (route.geo_json?.total_distance_km || 0), 0).toFixed(1) || '0.0'
const calculateTotalPackages = (routes: any[]) => routes?.reduce((sum, route) => sum + (route.geo_json?.package_count || 0), 0) || 0
const calculateTotalWeight = (routes: any[]) => {
  return routes?.reduce((sum, route) => {
    if (route.geo_json?.total_weight !== undefined) {
      return sum + route.geo_json.total_weight
    }
    const routeWeight = route.packages?.reduce((weight: number, pkg: any) => weight + (pkg.weight || 0), 0) || 0
    return sum + routeWeight
  }, 0).toFixed(1) || '0.0'
}

const calculateAvgDistance = (routes: any[]) => {
  const total = parseFloat(calculateTotalDistance(routes))
  const packages = calculateTotalPackages(routes)
  return packages > 0 ? (total / packages).toFixed(2) : '0.00'
}

const formatRoutePackageCount = (route: any) => route.geo_json?.package_count ?? route.packages?.length ?? 0
const formatRouteDistance = (route: any) => (route.geo_json?.total_distance_km ?? 0).toFixed(1)
const formatRouteWeight = (route: any) => {
  if (route.geo_json?.total_weight !== undefined) {
    return route.geo_json.total_weight.toFixed(1)
  }
  if (!route.packages?.length) {
    return '0.0'
  }
  return route.packages.reduce((sum: number, pkg: any) => sum + (pkg.weight || 0), 0).toFixed(1)
}

const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    READY: '已就绪',
    COMPLETED: '已完成',
    FAILED: '调度失败',
    RUNNING: '执行中'
  }
  return map[status] || status
}
</script>

<style scoped>
.history { display: flex; flex-direction: column; gap: 20px; }
.glass-card { background: rgba(255,255,255,0.9); backdrop-filter: blur(20px); border-radius: 16px; padding: 24px; box-shadow: 0 8px 32px rgba(0,0,0,0.1); }
h2, h3, h4 { margin: 0; }

.header { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; }
.header-text { max-width: 520px; }
.header-note { margin-top: 6px; color: #4a5568; font-size: 14px; line-height: 1.4; }
.header-actions { display: flex; gap: 12px; flex-wrap: wrap; }

.single-view { display: flex; flex-direction: column; gap: 20px; }
.section-note { margin: 6px 0 12px; color: #718096; font-size: 13px; }
.stats-overview { margin-bottom: 8px; }

.history-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px; }
.plan-card { transition: all 0.3s; }
.plan-card:hover { transform: translateY(-4px); box-shadow: 0 12px 40px rgba(102, 126, 234, 0.2); }

.plan-header { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; margin-bottom: 12px; }
.plan-time { font-size: 13px; color: #718096; margin-top: 4px; }

.plan-metrics { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-bottom: 12px; }
.mini-metric { display: flex; flex-direction: column; padding: 8px; background: rgba(102, 126, 234, 0.05); border-radius: 6px; }
.mini-metric .label { font-size: 12px; color: #718096; margin-bottom: 4px; }
.mini-metric .value { font-size: 18px; font-weight: bold; color: #667eea; }

.plan-params { display: flex; gap: 8px; flex-wrap: wrap; }
.plan-actions { display: flex; justify-content: flex-end; margin-top: 12px; }
.plan-actions .el-button { padding: 0; color: #4c51bf; }

.compare-view { display: flex; flex-direction: column; gap: 20px; }
.compare-selector { margin-bottom: 8px; }
.compare-selector h3 { margin-bottom: 16px; }
.el-checkbox-group { display: flex; flex-direction: column; gap: 12px; }

.compare-content { display: flex; flex-direction: column; gap: 20px; }
.compare-chart, .compare-table { margin-top: 0; }

.empty-history { display: flex; flex-direction: column; gap: 12px; align-items: flex-start; }
.empty-history h3 { color: #102a43; }
.empty-history p { margin: 0; color: #52606d; line-height: 1.6; }
.empty-link { color: #184a68; text-decoration: none; font-weight: 600; }

.detail-descriptions { margin-bottom: 16px; }
.route-list h4 { margin-bottom: 12px; font-size: 16px; }
.route-list p { margin: 0 0 6px; font-size: 14px; color: #2d3748; }
.empty-state { color: #718096; font-size: 13px; padding: 12px 0; }

.best { color: #48bb78; font-weight: bold; }

@media (max-width: 640px) {
  .header { flex-direction: column; }
  .header-actions { width: 100%; justify-content: flex-start; }
  .header-actions .el-button { flex: 1; }
}
</style>
