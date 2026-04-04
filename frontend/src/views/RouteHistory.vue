<template>
  <div class="history page-shell">
    <section class="section-card header">
      <div class="header-text">
        <h1>调度历史</h1>
        <p class="header-note">已完成计划按时间排序，点开即可复盘。</p>
      </div>
      <div class="header-actions">
        <el-button @click="loadPlans">刷新记录</el-button>
        <el-button type="primary" @click="compareMode = !compareMode">
          {{ compareMode ? '退出复盘对比' : '进入复盘对比' }}
        </el-button>
      </div>
    </section>

    <section v-if="!loading && !loadError && plans.length === 0" class="section-card empty-history">
      <h3>还没有已完成的调度记录</h3>
      <p>先前往调度中心重置演示数据并发起一次调度，完成后这里会出现可复盘的路线记录。</p>
      <router-link class="empty-link" :to="ONBOARDING_STEPS[0]?.path || '/dispatch'">
        {{ ONBOARDING_STEPS[0]?.actionLabel || '前往调度中心' }}
      </router-link>
    </section>

    <section v-else-if="loading" class="section-card empty-history">
      <h3>正在加载历史记录</h3>
      <p>请稍候，系统正在读取已完成的调度计划。</p>
    </section>

    <section v-else-if="loadError" class="section-card empty-history">
      <h3>历史记录加载失败</h3>
      <p>{{ loadError }}</p>
      <router-link class="empty-link" to="/dispatch">前往调度中心</router-link>
    </section>

    <div v-else-if="!compareMode" class="single-view">
      <section class="stats-overview section-card">
        <h3>历史调度趋势</h3>
        <p class="section-note">按创建时间查看已完成记录。</p>
        <div ref="trendChartRef" style="height: 300px"></div>
      </section>

      <div class="history-grid">
        <div v-for="plan in plans" :key="plan.id" class="plan-card section-card">
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
          </div>
          <div class="plan-actions">
            <el-button type="text" @click.stop="openPlanDetail(plan)">查看复盘</el-button>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="compare-view">
      <div class="compare-selector section-card">
        <h3>选择复盘对比方案（最多3个）</h3>
        <el-checkbox-group v-model="selectedPlans" :max="3">
          <el-checkbox v-for="plan in plans" :key="plan.id" :label="plan.id" :disabled="selectedPlans.length >= 3 && !selectedPlans.includes(plan.id)">
            {{ plan.title }} - {{ formatDate(plan.created_at) }}
          </el-checkbox>
        </el-checkbox-group>
      </div>

      <div v-if="selectedPlans.length >= 2" class="compare-content">
        <div class="compare-chart section-card">
          <h3>方案复盘对比</h3>
          <div ref="compareChartRef" style="height: 350px"></div>
        </div>

        <div class="compare-table section-card">
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
          <el-descriptions-item label="平均距离">{{ calculateAvgDistance(activePlan.routes) }} km</el-descriptions-item>
          <el-descriptions-item label="总重量">{{ calculateTotalWeight(activePlan.routes) }} kg</el-descriptions-item>
          <el-descriptions-item label="K值">{{ activePlan.algorithm_meta?.k || 'N/A' }}</el-descriptions-item>
          <el-descriptions-item label="遗传代数">{{ activePlan.algorithm_meta?.generations || 'N/A' }}</el-descriptions-item>
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
import { ref, onMounted, onBeforeUnmount, watch, computed, nextTick } from 'vue'
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
    loading.value = false
    await nextTick()
    if (plans.value.length > 0) {
      initTrendChart()
    }
  } catch (e) {
    console.error(e)
    loadError.value = '请刷新页面，或先前往调度中心生成第一条调度结果。'
  } finally {
    if (loading.value) {
      loading.value = false
    }
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
.history {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

h1,
h2,
h3,
h4 {
  margin: 0;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.75rem;
}

.header h1 {
  color: #102a43;
  font-size: clamp(1.8rem, 3vw, 2.4rem);
}

.header-text {
  max-width: 32rem;
}

.header-note {
  margin-top: 0.35rem;
  color: #52606d;
  line-height: 1.5;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.single-view,
.compare-view,
.compare-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.section-note {
  margin: 0.35rem 0 0.75rem;
  color: #6b7f92;
  font-size: 0.82rem;
}

.history-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(18rem, 1fr));
  gap: 1rem;
}

.plan-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.plan-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 16px 32px rgba(15, 23, 42, 0.08);
}

.plan-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.75rem;
  margin-bottom: 0.9rem;
}

.plan-time {
  font-size: 0.82rem;
  color: #6b7f92;
  margin-top: 0.25rem;
}

.plan-metrics {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.75rem;
}

.mini-metric {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 0.75rem;
  background: rgba(247, 250, 252, 0.92);
  border-radius: 0.9rem;
  border: 1px solid rgba(24, 74, 104, 0.08);
}

.mini-metric .label {
  font-size: 0.78rem;
  color: #6b7f92;
}

.mini-metric .value {
  font-size: 1.05rem;
  font-weight: 700;
  color: #184a68;
}

.plan-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 0.9rem;
}

.plan-actions .el-button { padding: 0; color: #4c51bf; }

.compare-selector h3 { margin-bottom: 1rem; }
.el-checkbox-group { display: flex; flex-direction: column; gap: 12px; }

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
  .plan-metrics { grid-template-columns: 1fr; }
}
</style>
