<template>
  <div class="analytics page-shell">
    <section class="page-hero">
      <div>
        <span class="eyebrow">运营分析</span>
        <h1>区分实测与估算。</h1>
        <p class="page-summary">先看接口返回的实际数据，再看演示推导。</p>
      </div>
      <el-button @click="loadData">刷新数据</el-button>
    </section>

    <el-alert v-if="loadError" type="error" :closable="false" show-icon>
      <template #title>运营分析加载失败</template>
      请稍后重试，或先前往调度中心生成一条新的调度结果。{{ loadError }}
    </el-alert>

    <el-alert v-else-if="loading" type="info" :closable="false" show-icon>
      <template #title>正在加载运营分析</template>
      正在读取调度计划、包裹和快递员数据。
    </el-alert>

    <section class="section-card">
      <header class="section-head">
        <div>
          <h2>实际数据</h2>
          <p>包裹、快递员和已完成计划的接口结果。</p>
        </div>
      </header>

      <div class="kpi-grid">
        <article class="kpi-card" v-for="item in factualKpis" :key="item.label">
          <span class="kpi-label">{{ item.label }}</span>
          <strong class="kpi-value">{{ item.value }}</strong>
          <span v-if="item.caption" class="kpi-caption">{{ item.caption }}</span>
        </article>
      </div>
    </section>

    <section class="section-card">
      <header class="section-head">
        <div>
          <h2>演示估算</h2>
          <p>帮助理解优化幅度，不代表实测产出。</p>
        </div>
      </header>

      <div class="estimate-meta">
        <span class="estimate-chip">演示估算</span>
        <p>基线距离按当前路线上浮 20%，成本按每公里 6 元换算。</p>
      </div>

      <div class="estimate-grid">
        <article class="estimate-card">
          <span class="kpi-label">估算基线路径距离</span>
          <strong class="kpi-value">{{ summary.estimated.baselineDistance }}</strong>
          <span class="kpi-caption">km</span>
        </article>
        <article class="estimate-card">
          <span class="kpi-label">估算节省距离</span>
          <strong class="kpi-value">{{ summary.estimated.savedDistance }}</strong>
          <span class="kpi-caption">km</span>
        </article>
        <article class="estimate-card">
          <span class="kpi-label">估算节省率</span>
          <strong class="kpi-value">{{ summary.estimated.savedRate }}</strong>
          <span class="kpi-caption">%</span>
        </article>
        <article class="estimate-card">
          <span class="kpi-label">估算成本节省</span>
          <strong class="kpi-value">{{ summary.estimated.savedCost }}</strong>
          <span class="kpi-caption">元</span>
        </article>
      </div>
    </section>

    <section v-if="!loadError && summary.factual.totalPlans === 0" class="section-card empty-panel">
      <h2>还没有可分析的调度结果</h2>
      <p>先在调度中心生成一条路线结果，分析图表和工作量统计才会出现。</p>
      <router-link class="refresh-link" to="/dispatch">前往调度中心</router-link>
    </section>

    <section v-else-if="!loadError" class="charts-grid">
      <article class="section-card">
        <header class="section-head">
          <div>
            <h2>最近调度趋势</h2>
            <p>最近 10 次路线距离与包裹数。</p>
          </div>
        </header>
        <div ref="trendChartRef" class="chart-host"></div>
      </article>

      <article class="section-card">
        <header class="section-head">
          <div>
            <h2>最新调度工作量</h2>
            <p>最近一次计划的快递员包裹量。</p>
          </div>
        </header>
        <div ref="courierChartRef" class="chart-host"></div>
      </article>
    </section>

    <section v-if="!loadError && summary.factual.totalPlans > 0" class="charts-grid">
      <article class="section-card">
        <header class="section-head">
          <div>
            <h2>包裹状态分布</h2>
            <p>当前包裹状态。</p>
          </div>
        </header>
        <div ref="packageStatusChartRef" class="chart-host compact"></div>
      </article>

      <article class="section-card">
        <header class="section-head">
          <div>
            <h2>快递员状态分布</h2>
            <p>当前快递员状态。</p>
          </div>
        </header>
        <div ref="courierStatusChartRef" class="chart-host compact"></div>
      </article>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'

import { buildAnalyticsSummary, getCompletedPlans, getRecentCompletedPlans } from '../lib/analytics'

const summary = ref(
  buildAnalyticsSummary({
    plans: [],
    packages: [],
    couriers: []
  })
)

const trendChartRef = ref()
const courierChartRef = ref()
const packageStatusChartRef = ref()
const courierStatusChartRef = ref()
const loading = ref(true)
const loadError = ref('')

const factualKpis = computed(() => [
  {
    label: '包裹总数',
    value: summary.value.factual.totalPackages,
    caption: ''
  },
  {
    label: '待调度包裹',
    value: summary.value.factual.pendingPackages,
    caption: '待调度状态'
  },
  {
    label: '快递员总数',
    value: summary.value.factual.totalCouriers,
    caption: ''
  },
  {
    label: '历史计划数',
    value: summary.value.factual.totalPlans,
    caption: '已生成路线'
  },
  {
    label: '累计路线距离',
    value: summary.value.factual.totalOptimizedDistance,
    caption: '历史路线总和'
  },
  {
    label: '平均每车包裹数',
    value: summary.value.factual.averagePackagesPerCourier,
    caption: '最近一次计划'
  }
])

const loadData = async () => {
  loading.value = true
  loadError.value = ''
  try {
    const [plansRes, packagesRes, couriersRes] = await Promise.all([
      axios.get('/api/v1/dispatch/plans'),
      axios.get('/api/v1/delivery/packages'),
      axios.get('/api/v1/delivery/couriers')
    ])

    const plans = plansRes.data
    const packages = packagesRes.data
    const couriers = couriersRes.data
    const completedPlans = getCompletedPlans(plans)

    summary.value = buildAnalyticsSummary({ plans, packages, couriers })

    const latestRanking =
      completedPlans[0]?.routes
        ?.map((route: any) => {
          const courier = couriers.find((item: any) => item.id === route.courier_id)
          return {
            name: courier?.name || `快递员 ${route.courier_id}`,
            deliveredCount: route.geo_json?.package_count || 0
          }
        })
        .sort((left: any, right: any) => right.deliveredCount - left.deliveredCount) || []

    initTrendChart(plans)
    initCourierChart(latestRanking)
    initPackageStatusChart(packages)
    initCourierStatusChart(couriers)
  } catch (error) {
    console.error(error)
    loadError.value = error instanceof Error ? error.message : '无法连接到分析接口。'
  } finally {
    loading.value = false
  }
}

const initTrendChart = (plans: any[]) => {
  if (!trendChartRef.value) return
  const chart = echarts.init(trendChartRef.value)

  const recentPlans = getRecentCompletedPlans(plans, 10)
  const dates = recentPlans.map((plan: any) => new Date(plan.created_at).toLocaleDateString('zh-CN'))
  const distances = recentPlans.map(
    (plan: any) =>
      plan.routes?.reduce(
        (sum: number, route: any) => sum + (route.geo_json?.total_distance_km || 0),
        0
      ) || 0
  )
  const packages = recentPlans.map(
    (plan: any) => plan.routes?.reduce((sum: number, route: any) => sum + (route.geo_json?.package_count || 0), 0) || 0
  )

  chart.setOption({
    color: ['#1f6f8b', '#829ab1'],
    tooltip: { trigger: 'axis' },
    legend: { data: ['路线距离', '包裹数'], top: 0 },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '18%', containLabel: true },
    xAxis: { type: 'category', data: dates },
    yAxis: [{ type: 'value', name: '距离(km)' }, { type: 'value', name: '包裹数' }],
    series: [
      { name: '路线距离', type: 'line', data: distances, smooth: true },
      { name: '包裹数', type: 'bar', yAxisIndex: 1, data: packages }
    ]
  })
}

const initCourierChart = (ranking: any[]) => {
  if (!courierChartRef.value) return
  const chart = echarts.init(courierChartRef.value)

  const topCouriers = ranking.slice(0, 10).reverse()

  chart.setOption({
    color: ['#184a68'],
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '6%', bottom: '3%', top: '6%', containLabel: true },
    xAxis: { type: 'value', name: '包裹数' },
    yAxis: { type: 'category', data: topCouriers.map((item: any) => item.name) },
    series: [
      {
        type: 'bar',
        data: topCouriers.map((item: any) => item.deliveredCount),
        label: { show: true, position: 'right' }
      }
    ]
  })
}

const initPackageStatusChart = (packages: any[]) => {
  if (!packageStatusChartRef.value) return
  const chart = echarts.init(packageStatusChartRef.value)

  const statusCount: Record<string, number> = {}
  packages.forEach((item: any) => {
    statusCount[item.status] = (statusCount[item.status] || 0) + 1
  })

  const statusMap: Record<string, string> = {
    PENDING: '待调度',
    ASSIGNED: '已分配',
    IN_TRANSIT: '配送中',
    DELIVERED: '已送达'
  }

  chart.setOption({
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left' },
    series: [
      {
        type: 'pie',
        radius: ['42%', '72%'],
        itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
        data: Object.entries(statusCount).map(([key, value]) => ({
          name: statusMap[key] || key,
          value
        }))
      }
    ]
  })
}

const initCourierStatusChart = (couriers: any[]) => {
  if (!courierStatusChartRef.value) return
  const chart = echarts.init(courierStatusChartRef.value)

  const statusCount: Record<string, number> = {}
  couriers.forEach((item: any) => {
    statusCount[item.status] = (statusCount[item.status] || 0) + 1
  })

  const statusMap: Record<string, string> = {
    AVAILABLE: '空闲',
    BUSY: '忙碌',
    OFF_DUTY: '离线'
  }

  chart.setOption({
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left' },
    series: [
      {
        type: 'pie',
        radius: ['42%', '72%'],
        itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
        data: Object.entries(statusCount).map(([key, value]) => ({
          name: statusMap[key] || key,
          value
        }))
      }
    ]
  })
}

onMounted(() => loadData())
</script>

<style scoped>
.analytics {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.page-hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1rem;
}

.eyebrow {
  display: inline-flex;
  margin-bottom: 0.75rem;
  color: #486581;
  font-size: 0.82rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.page-hero h1 {
  margin: 0 0 0.5rem;
  color: #102a43;
  font-size: clamp(1.8rem, 3vw, 2.4rem);
}

.page-summary {
  margin: 0;
  max-width: 42rem;
  color: #52606d;
  line-height: 1.6;
}

.section-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.section-head h2 {
  margin: 0 0 0.25rem;
  color: #102a43;
  font-size: 1.1rem;
}

.section-head p {
  margin: 0;
  color: #52606d;
  line-height: 1.5;
}

.estimate-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
  align-items: center;
  margin-bottom: 1rem;
}

.estimate-chip {
  display: inline-flex;
  align-items: center;
  min-height: 1.8rem;
  padding: 0 0.75rem;
  border-radius: 999px;
  background: rgba(220, 166, 30, 0.16);
  color: #946200;
  font-size: 0.82rem;
  font-weight: 600;
}

.estimate-meta p {
  margin: 0;
  color: #6b7280;
  line-height: 1.45;
}

.kpi-grid,
.estimate-grid,
.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.kpi-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.kpi-card,
.estimate-card {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  padding: 1rem;
  border-radius: 1rem;
  background: rgba(247, 250, 252, 0.92);
  border: 1px solid rgba(24, 74, 104, 0.08);
}

.estimate-card {
  background: rgba(255, 250, 235, 0.7);
  border-color: rgba(220, 166, 30, 0.22);
}

.kpi-label {
  color: #486581;
  font-size: 0.88rem;
}

.kpi-value {
  color: #102a43;
  font-size: clamp(1.6rem, 2.6vw, 2.1rem);
}

.kpi-caption {
  color: #52606d;
  line-height: 1.5;
}

.chart-host {
  height: 20rem;
}

.chart-host.compact {
  height: 18rem;
}

.empty-panel {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.empty-panel h2 {
  margin: 0;
  color: #102a43;
}

.empty-panel p {
  margin: 0;
  color: #52606d;
  line-height: 1.6;
}

.refresh-link {
  color: #184a68;
  font-weight: 600;
  text-decoration: none;
}

@media (max-width: 960px) {
  .page-hero,
  .kpi-grid,
  .estimate-grid,
  .charts-grid {
    grid-template-columns: 1fr;
  }

  .page-hero {
    align-items: flex-start;
  }
}
</style>
