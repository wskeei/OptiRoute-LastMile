<template>
  <div class="dispatch page-shell">
    <section class="page-hero">
      <div>
        <span class="eyebrow">调度中心</span>
        <h1>准备样本后直接发起调度。</h1>
        <p class="page-summary">路线结果会在地图和状态区持续刷新。</p>
      </div>

      <div class="hero-actions">
        <el-button type="warning" size="large" :loading="resetting" :disabled="loading" @click="resetDemo">
          重置数据
        </el-button>
        <el-button type="primary" size="large" :loading="loading" :disabled="!canDispatch" @click="startDispatch">
          开始调度
        </el-button>
      </div>
    </section>

    <section class="dispatch-layout">
      <article class="section-card map-panel">
        <header class="section-head">
          <div>
            <h2>路线地图</h2>
            <p>最近一次结果会在这里刷新。</p>
          </div>
        </header>

        <div class="map-shell">
          <div ref="mapRef" class="map-view"></div>

          <aside class="info-panel">
            <section class="info-block">
              <h3>当前样本</h3>
              <div class="fact-list">
                <div class="fact-item">
                  <span>待调度包裹</span>
                  <strong>{{ pendingPackageCount }}</strong>
                </div>
                <div class="fact-item">
                  <span>可用快递员</span>
                  <strong>{{ availableCourierCount }}</strong>
                </div>
                <div class="fact-item">
                  <span>配送站</span>
                  <strong>{{ stationName }}</strong>
                </div>
              </div>
            </section>

            <details class="info-block truth-details">
              <summary>查看执行说明</summary>
              <ul class="note-list">
                <li v-for="item in DISPATCH_TRUTH_NOTES" :key="item">{{ item }}</li>
              </ul>
            </details>

            <section v-if="inlineStatus" class="info-block">
              <h3>{{ inlineStatus.title }}</h3>
              <p class="status-copy">{{ inlineStatus.message }}</p>
              <div v-if="inlineStatus.action === 'retry-dispatch'" class="status-actions">
                <el-button type="primary" size="small" :disabled="!canDispatch || loading" @click="startDispatch">
                  重新发起调度
                </el-button>
              </div>
            </section>

            <section v-if="loading" class="info-block">
              <h3>调度进度</h3>
              <el-steps :active="step" direction="vertical" size="small">
                <el-step title="准备数据" />
                <el-step title="聚类分配" />
                <el-step title="路径优化" />
                <el-step title="结果输出" />
              </el-steps>
            </section>

            <section v-else-if="result" class="info-block">
              <h3>本次结果</h3>
              <div class="result-grid">
                <div>
                  <span>路线数</span>
                  <strong>{{ result.routeCount }}</strong>
                </div>
                <div>
                  <span>总距离</span>
                  <strong>{{ result.totalDistance }} km</strong>
                </div>
                <div>
                  <span>最新迭代进度</span>
                  <strong>{{ result.generation || 0 }} 代</strong>
                </div>
              </div>
            </section>
          </aside>
        </div>
      </article>

    </section>

    <section v-if="!canDispatch" class="section-card helper-card">
      <h2>先准备样本</h2>
      <p>需要待调度包裹和可用快递员后才能开始。最简单的做法是点击“重置数据”。</p>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import axios from 'axios'
import L from 'leaflet'
import 'leaflet-ant-path'
import { ElMessage } from 'element-plus'

import { DISPATCH_TRUTH_NOTES } from '../lib/ux'
import { sortPlansByNewest } from '../lib/analytics'

interface DispatchResult {
  routeCount: number
  totalDistance: string
  generation: number
}

interface InlineStatus {
  title: string
  message: string
  action?: 'retry-dispatch'
}

const loading = ref(false)
const resetting = ref(false)
const step = ref(0)
const batchName = ref('')
const pendingPackageCount = ref(0)
const availableCourierCount = ref(0)
const stationName = ref('人民广场配送站')
const result = ref<DispatchResult | null>(null)
const inlineStatus = ref<InlineStatus | null>(null)
const mapRef = ref()
const stationId = ref(1)
const allPackages = ref<any[]>([])

let map: any = null
const packageLayerGroup = ref<any>(null)
const routeLayerGroup = ref<any>(null)

const canDispatch = computed(() => pendingPackageCount.value > 0 && availableCourierCount.value > 0)

const setInlineStatus = (title: string, message: string, action?: 'retry-dispatch') => {
  inlineStatus.value = { title, message, action }
}

const fetchDispatchContext = async () => {
  const [packagesRes, couriersRes] = await Promise.all([
    axios.get('/api/v1/delivery/packages'),
    axios.get('/api/v1/delivery/couriers')
  ])

  allPackages.value = packagesRes.data
  pendingPackageCount.value = packagesRes.data.filter((item: any) => item.status === 'PENDING').length
  availableCourierCount.value = couriersRes.data.filter((item: any) => item.status === 'AVAILABLE').length
}

const drawPackageMarkers = () => {
  if (!map) return

  if (!packageLayerGroup.value) {
    packageLayerGroup.value = L.layerGroup().addTo(map)
  } else {
    packageLayerGroup.value.clearLayers()
  }

  const pendingPackages = allPackages.value.filter((item: any) => item.status === 'PENDING')

  pendingPackages.forEach((item: any) => {
    L.circleMarker([item.latitude, item.longitude], {
      radius: 6,
      fillColor: '#1f6f8b',
      color: '#ffffff',
      weight: 2,
      opacity: 1,
      fillOpacity: 0.9
    })
      .addTo(packageLayerGroup.value)
      .bindPopup(
        `<b>${item.recipient_name}</b><br>单号: ${item.tracking_number}<br>重量: ${item.weight}kg`
      )
  })
}

onMounted(async () => {
  batchName.value = `调度计划 ${new Date().toLocaleString('zh-CN')}`

  try {
    await fetchDispatchContext()
    inlineStatus.value = null

    map = L.map(mapRef.value).setView([31.2304, 121.4737], 12)
    L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png').addTo(map)

    const stationIcon = L.divIcon({
      html: '<div style="background:#184a68;width:18px;height:18px;border-radius:50%;border:3px solid white;box-shadow:0 2px 12px rgba(16,42,67,0.25);"></div>',
      iconSize: [18, 18]
    })
    L.marker([31.2304, 121.4737], { icon: stationIcon }).addTo(map).bindPopup(stationName.value)

    drawPackageMarkers()
    await restoreLatestPlan()

    setTimeout(() => {
      map.invalidateSize()
    }, 200)
  } catch (error) {
    console.error(error)
    setInlineStatus('调度中心加载失败', '无法读取当前样本数据，请刷新页面后重试。')
  }
})

const restoreLatestPlan = async () => {
  const plansRes = await axios.get('/api/v1/dispatch/plans')
  const activePlans = sortPlansByNewest(plansRes.data).filter((plan: any) =>
    ['READY', 'COMPLETED', 'OPTIMIZING'].includes(plan.status)
  )

  if (activePlans.length === 0) {
    return
  }

  const latestPlan = activePlans[0]
  if (latestPlan.routes && latestPlan.routes.length > 0) {
    drawRoutes(latestPlan.routes)
    step.value = latestPlan.status === 'OPTIMIZING' ? 2 : 3
    ElMessage.success('已恢复最近一次调度结果')
  }
}

const startDispatch = async () => {
  if (!canDispatch.value) {
    ElMessage.warning('请先准备待调度包裹和可用快递员')
    return
  }

  loading.value = true
  step.value = 1
  result.value = null
  inlineStatus.value = null

  try {
    ElMessage.info('正在创建调度计划...')
    const response = await axios.post('/api/v1/dispatch/plans', {
      title: batchName.value,
      station_id: stationId.value
    })

    step.value = 2
    ElMessage.success('计划已创建，正在等待路线结果...')
    await pollStatus(response.data.id)
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '调度失败')
    loading.value = false
    step.value = 0
    setInlineStatus('调度创建失败', '当前无法创建新的调度计划，请稍后重试。', 'retry-dispatch')
  }
}

const pollStatus = async (planId: number) => {
  const interval = setInterval(async () => {
    try {
      const response = await axios.get(`/api/v1/dispatch/plans/${planId}`)

      if (response.data.routes && response.data.routes.length > 0) {
        drawRoutes(response.data.routes)
      }

      if (response.data.status === 'READY' || response.data.status === 'COMPLETED') {
        clearInterval(interval)
        step.value = 3
        loading.value = false

        if (!response.data.routes || response.data.routes.length === 0) {
          ElMessage.error('调度未生成路线，请先检查演示样本数据')
          step.value = 0
        } else {
          ElMessage.success('路线结果已生成')
        }
      }
    } catch (error) {
      clearInterval(interval)
      loading.value = false
      console.error(error)
      setInlineStatus('调度状态获取失败', '可以重新发起调度，或先点击“重置数据”刷新样本。', 'retry-dispatch')
    }
  }, 1000)
}

const drawRoutes = (routes: any[]) => {
  if (!map) return

  if (!routeLayerGroup.value) {
    routeLayerGroup.value = L.layerGroup().addTo(map)
  } else {
    routeLayerGroup.value.clearLayers()
  }

  const fallbackColors = ['#184a68', '#4c956c', '#b08968', '#c05621', '#6b7280']
  let totalDistance = 0
  let maxGeneration = 0

  routes.forEach((route, index) => {
    if (!route.geo_json?.coordinates) return

    const latlngs = route.geo_json.coordinates.map((coord: any) => [coord[1], coord[0]])
    const color = route.geo_json.color || fallbackColors[index % fallbackColors.length]
    const isOptimizing = route.geo_json.status === 'optimizing'

    if (route.geo_json.generation > maxGeneration) {
      maxGeneration = route.geo_json.generation
    }

    try {
      if ((L as any).polyline.antPath) {
        ;(L as any).polyline.antPath(latlngs, {
          color,
          weight: 4,
          opacity: isOptimizing ? 0.5 : 0.72,
          pulseColor: '#ffffff',
          delay: isOptimizing ? 420 : 800,
          dashArray: isOptimizing ? [10, 18] : [10, 10]
        }).addTo(routeLayerGroup.value)
      } else {
        L.polyline(latlngs, {
          color,
          weight: 4,
          opacity: 0.72
        }).addTo(routeLayerGroup.value)
      }

      const orderedPackages = route.geo_json.packages_ordered || []

      route.geo_json.coordinates.slice(1, -1).forEach((coord: any, packageIndex: number) => {
        const icon = L.divIcon({
          html: `<div style="background:${color};color:white;width:22px;height:22px;border-radius:999px;border:2px solid white;box-shadow:0 2px 6px rgba(0,0,0,0.25);display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:bold;">${packageIndex + 1}</div>`,
          iconSize: [22, 22]
        })

        const marker = L.marker([coord[1], coord[0]], { icon }).addTo(routeLayerGroup.value)
        const packageInfo = orderedPackages[packageIndex]

        if (packageInfo) {
          marker.bindPopup(
            `<div style="font-size:13px;"><b>${packageIndex + 1}. ${packageInfo.recipient_name || '收件人'}</b><br><span style="color:#52606d">单号: ${packageInfo.tracking_number || '-'}</span><br><span style="color:#52606d">重量: ${packageInfo.weight || 1}kg</span><br><span style="color:#52606d">${packageInfo.address || ''}</span></div>`
          )
        }
      })

      if (route.geo_json.cluster_center) {
        const [centerLat, centerLon] = route.geo_json.cluster_center
        const packageCount = route.geo_json.package_count || 10
        const radius = 5000 + packageCount * 100

        L.circle([centerLat, centerLon], {
          radius,
          color,
          fillColor: color,
          fillOpacity: 0.05,
          weight: 1,
          dashArray: '5, 5'
        }).addTo(routeLayerGroup.value)
      }

      totalDistance += route.geo_json.total_distance_km || 0
    } catch (error) {
      console.error(error)
    }
  })

  result.value = {
    routeCount: routes.length,
    totalDistance: totalDistance.toFixed(1),
    generation: maxGeneration
  }
}

const resetDemo = async () => {
  resetting.value = true

  try {
    await axios.post('/api/v1/dispatch/reset-demo')
    ElMessage.success('演示样本已更新，可以重新发起调度')
    result.value = null
    step.value = 0
    inlineStatus.value = null

    await fetchDispatchContext()

    if (routeLayerGroup.value) {
      routeLayerGroup.value.clearLayers()
    }
    if (packageLayerGroup.value) {
      packageLayerGroup.value.clearLayers()
    }

    drawPackageMarkers()
  } catch (error: any) {
    console.error(error)
    ElMessage.error(error.response?.data?.detail || `重置失败: ${error.message || '未知错误'}`)
    setInlineStatus('重置数据失败', '请稍后重试；如果问题持续存在，请刷新页面后再操作。')
  } finally {
    resetting.value = false
  }
}
</script>

<style scoped>
.dispatch {
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

.hero-actions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  align-items: flex-end;
}

.dispatch-layout {
  display: block;
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

.map-panel {
  min-height: 38rem;
}

.map-shell {
  min-height: 0;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 18rem;
  gap: 1rem;
}

.map-view {
  min-height: 32rem;
  border-radius: 1rem;
  overflow: hidden;
  border: 1px solid rgba(24, 74, 104, 0.08);
}

.info-panel {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.info-block {
  padding: 1rem;
  border-radius: 1rem;
  background: rgba(247, 250, 252, 0.92);
  border: 1px solid rgba(24, 74, 104, 0.08);
}

.info-block h3 {
  margin: 0 0 0.85rem;
  color: #102a43;
  font-size: 1rem;
}

.fact-list,
.result-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.75rem;
}

.fact-item,
.result-grid div {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.fact-item span,
.result-grid span {
  color: #486581;
  font-size: 0.85rem;
}

.fact-item strong,
.result-grid strong {
  color: #102a43;
  font-size: 1.25rem;
}

.note-list {
  margin: 0;
  padding-left: 1.1rem;
  color: #243b53;
  line-height: 1.7;
}

.truth-details summary {
  cursor: pointer;
  color: #184a68;
  font-weight: 600;
  list-style: none;
}

.truth-details summary::-webkit-details-marker {
  display: none;
}

.truth-details[open] summary {
  margin-bottom: 0.65rem;
}

.status-copy {
  margin: 0;
  color: #52606d;
  line-height: 1.6;
}

.status-actions {
  margin-top: 0.75rem;
}

.helper-card {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.helper-card h2,
.helper-card p {
  margin: 0;
}

@media (max-width: 1100px) {
  .dispatch-layout,
  .map-shell {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 900px) {
  .page-hero {
    align-items: flex-start;
    flex-direction: column;
  }

  .hero-actions {
    align-items: flex-start;
  }

  .hero-note {
    justify-content: flex-start;
  }

  .hero-note p {
    text-align: left;
  }
}
</style>
