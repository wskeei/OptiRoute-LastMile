<template>
  <div class="dashboard page-shell">
    <section class="page-hero">
      <div>
        <span class="eyebrow">任务概览</span>
        <h1>先完成一次调度，再看监控和复盘。</h1>
        <p class="page-summary">
          这个首页不再承担“炫技展示”，只帮助你确认演示环境状态并进入下一步。
        </p>
      </div>
      <router-link class="primary-link" to="/dispatch">进入调度中心</router-link>
    </section>

    <el-alert type="info" :closable="false" show-icon>
      <template #title>当前是演示环境</template>
      路线、距离和状态来自后端真实结果；演示数据来自“重置演示数据”接口。
    </el-alert>

    <el-alert v-if="loadError" type="error" :closable="false" show-icon>
      <template #title>任务概览加载失败</template>
      请刷新页面或前往调度中心重新开始。{{ loadError }}
    </el-alert>

    <el-alert v-else-if="loading" type="info" :closable="false" show-icon>
      <template #title>正在加载任务概览</template>
      正在读取样本、历史计划和工作量数据。
    </el-alert>

    <section class="workflow-grid">
      <article class="workflow-card section-card">
        <header class="section-head">
          <div>
            <h2>首次使用流程</h2>
            <p>按顺序完成这三步，30 秒内可以得到第一条路线结果。</p>
          </div>
        </header>

        <ol class="step-list">
          <li v-for="step in ONBOARDING_STEPS" :key="step.title" class="step-item">
            <div>
              <strong>{{ step.title }}</strong>
              <p>{{ step.description }}</p>
            </div>
            <router-link class="text-link" :to="step.path">{{ step.actionLabel }}</router-link>
          </li>
        </ol>
      </article>

      <article class="action-card section-card">
        <header class="section-head">
          <div>
            <h2>关键入口</h2>
            <p>所有主操作都放在可理解的按钮上，不再依赖整块卡片点击。</p>
          </div>
        </header>

        <div class="action-list">
          <router-link class="action-link" to="/dispatch">
            <span>重置数据或开始调度</span>
            <small>调度中心</small>
          </router-link>
          <router-link class="action-link" to="/monitor">
            <span>查看最近一次路线</span>
            <small>路线监控</small>
          </router-link>
          <router-link class="action-link" to="/history">
            <span>打开历史计划详情</span>
            <small>调度历史</small>
          </router-link>
        </div>
      </article>
    </section>

    <section class="stats-grid">
      <article class="metric-card section-card">
        <span class="metric-label">包裹样本</span>
        <strong class="metric-value">{{ stats.totalPackages }}</strong>
        <p>当前数据库中的包裹总数</p>
      </article>
      <article class="metric-card section-card">
        <span class="metric-label">快递员样本</span>
        <strong class="metric-value">{{ stats.totalCouriers }}</strong>
        <p>可用于演示的快递员总数</p>
      </article>
      <article class="metric-card section-card">
        <span class="metric-label">历史调度</span>
        <strong class="metric-value">{{ stats.totalPlans }}</strong>
        <p>已有实际路线结果的调度计划</p>
      </article>
      <article class="metric-card section-card">
        <span class="metric-label">累计路线距离</span>
        <strong class="metric-value">{{ stats.optimizedDistance }}</strong>
        <p>来自历史调度结果的总距离（km）</p>
      </article>
    </section>

    <section v-if="!loadError && stats.totalPlans === 0" class="section-card empty-panel">
      <h2>还没有可复盘的调度结果</h2>
      <p>先去调度中心重置演示数据并发起一次调度，监控和排行图表才会出现。</p>
      <router-link class="primary-link" to="/dispatch">前往调度中心</router-link>
    </section>

    <section v-else-if="!loadError" class="chart-grid">
      <article class="section-card">
        <header class="section-head">
          <div>
            <h2>最近调度记录</h2>
            <p>展示最近 8 次实际调度的路线距离和包裹数。</p>
          </div>
        </header>
        <div ref="chartRef" class="chart-host"></div>
      </article>

      <article class="section-card">
        <header class="section-head">
          <div>
            <h2>最近工作量排行</h2>
            <p>使用后端返回的快递员完成量数据。</p>
          </div>
        </header>
        <div ref="courierChartRef" class="chart-host"></div>
      </article>
    </section>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'

import { getCompletedPlans, getRecentCompletedPlans } from '../lib/analytics'
import { ONBOARDING_STEPS } from '../lib/ux'

const stats = ref({
  totalPackages: 0,
  totalCouriers: 0,
  totalPlans: 0,
  optimizedDistance: '0.0'
})
const chartRef = ref()
const courierChartRef = ref()
const loading = ref(true)
const loadError = ref('')

onMounted(async () => {
  loading.value = true
  loadError.value = ''
  try {
    const [packagesRes, couriersRes, plansRes, rankRes] = await Promise.all([
      axios.get('/api/v1/delivery/packages'),
      axios.get('/api/v1/delivery/couriers'),
      axios.get('/api/v1/dispatch/plans'),
      axios.get('/api/v1/stats/courier-ranking')
    ])

    stats.value.totalPackages = packagesRes.data.length
    stats.value.totalCouriers = couriersRes.data.length

    const completedPlans = getCompletedPlans(plansRes.data)
    stats.value.totalPlans = completedPlans.length

    const totalDistance = completedPlans.reduce(
      (sum: number, plan: any) =>
        sum +
        (plan.routes?.reduce(
          (routeSum: number, route: any) => routeSum + (route.geo_json?.total_distance_km || 0),
          0
        ) || 0),
      0
    )
    stats.value.optimizedDistance = totalDistance.toFixed(1)

    if (chartRef.value && completedPlans.length > 0) {
      const chart = echarts.init(chartRef.value)
      const recentPlans = getRecentCompletedPlans(plansRes.data, 8)
      const dates = recentPlans.map((plan: any) => new Date(plan.created_at).toLocaleDateString('zh-CN'))
      const distances = recentPlans.map(
        (plan: any) =>
          plan.routes?.reduce(
            (sum: number, route: any) => sum + (route.geo_json?.total_distance_km || 0),
            0
          ) || 0
      )
      const packages = recentPlans.map(
        (plan: any) =>
          plan.routes?.reduce((sum: number, route: any) => sum + (route.geo_json?.package_count || 0), 0) || 0
      )

      chart.setOption({
        color: ['#1f6f8b', '#4c956c'],
        tooltip: { trigger: 'axis' },
        legend: { data: ['路线距离', '包裹数'], top: 0 },
        grid: { left: '3%', right: '4%', bottom: '3%', top: '18%', containLabel: true },
        xAxis: { type: 'category', data: dates },
        yAxis: [{ type: 'value', name: '距离(km)' }, { type: 'value', name: '包裹数' }],
        series: [
          { name: '路线距离', type: 'line', smooth: true, data: distances },
          { name: '包裹数', type: 'bar', yAxisIndex: 1, data: packages }
        ]
      })
    }

    if (courierChartRef.value && rankRes.data.length > 0) {
      const chart = echarts.init(courierChartRef.value)
      const topFive = rankRes.data
        .map((item: any) => ({ name: item.name, count: item.delivered_count }))
        .slice(0, 5)
        .reverse()

      chart.setOption({
        color: ['#184a68'],
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        grid: { left: '3%', right: '6%', bottom: '3%', top: '6%', containLabel: true },
        xAxis: { type: 'value', name: '送单量' },
        yAxis: { type: 'category', data: topFive.map((item: any) => item.name) },
        series: [
          {
            type: 'bar',
            data: topFive.map((item: any) => item.count),
            label: { show: true, position: 'right' }
          }
        ]
      })
    }
  } catch (error) {
    console.error(error)
    loadError.value = error instanceof Error ? error.message : '无法连接到概览接口。'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.page-hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1rem;
  padding: 1.5rem;
  border-radius: 1.5rem;
  background: linear-gradient(135deg, rgba(24, 74, 104, 0.1), rgba(76, 149, 108, 0.08));
  border: 1px solid rgba(24, 74, 104, 0.1);
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
  font-size: clamp(1.8rem, 3vw, 2.4rem);
  color: #102a43;
}

.page-summary {
  margin: 0;
  max-width: 42rem;
  color: #52606d;
  line-height: 1.6;
}

.primary-link,
.text-link,
.action-link {
  text-decoration: none;
}

.primary-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 2.75rem;
  padding: 0 1.25rem;
  border-radius: 999px;
  background: #184a68;
  color: #f7fafc;
  font-weight: 600;
}

.workflow-grid,
.chart-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.section-card {
  height: 100%;
}

.section-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.section-head h2 {
  margin: 0 0 0.25rem;
  color: #102a43;
  font-size: 1.15rem;
}

.section-head p {
  margin: 0;
  color: #52606d;
  line-height: 1.5;
}

.step-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 0;
  margin: 0;
  list-style: none;
}

.step-item {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem;
  border-radius: 1rem;
  background: rgba(224, 232, 240, 0.5);
}

.step-item strong {
  display: block;
  margin-bottom: 0.35rem;
  color: #102a43;
}

.step-item p {
  margin: 0;
  color: #52606d;
  line-height: 1.5;
}

.text-link {
  align-self: center;
  color: #184a68;
  font-weight: 600;
  white-space: nowrap;
}

.action-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.action-link {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  padding: 1rem;
  border-radius: 1rem;
  background: rgba(247, 250, 252, 0.9);
  border: 1px solid rgba(24, 74, 104, 0.08);
  color: #102a43;
}

.action-link small {
  color: #52606d;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1rem;
}

.metric-card {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.metric-label {
  color: #486581;
  font-size: 0.88rem;
}

.metric-value {
  color: #102a43;
  font-size: clamp(1.6rem, 3vw, 2.2rem);
}

.metric-card p {
  margin: 0;
  color: #52606d;
  line-height: 1.5;
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

.chart-host {
  height: 20rem;
}

@media (max-width: 960px) {
  .page-hero,
  .workflow-grid,
  .chart-grid,
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .page-hero {
    align-items: flex-start;
  }
}

@media (max-width: 640px) {
  .step-item {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
