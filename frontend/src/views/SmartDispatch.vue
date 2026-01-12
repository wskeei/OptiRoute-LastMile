<template>
  <div class="dispatch">
    <div class="dispatch-header glass-card">
      <h2>🤖 AI智能调度中心</h2>
      <div class="header-actions">
        <el-button type="warning" size="large" @click="resetDemo" :disabled="loading">🔄 重置演示数据</el-button>
        <el-button type="primary" size="large" :loading="loading" @click="startDispatch">
          🚀 开始AI调度
        </el-button>
      </div>
    </div>

    <div class="dispatch-content">
      <div class="map-panel glass-card">
        <h3>🗺️ 路径可视化</h3>
        <div class="map-container">
          <div ref="mapRef" class="map-view"></div>

          <div class="config-overlay glass-card">
            <h3>📋 调度配置</h3>
            <el-form label-width="100px" size="small">
              <el-form-item label="包裹数量">
                <el-input v-model="packageCount" disabled />
              </el-form-item>
              <el-form-item label="快递员">
                <el-input v-model="courierCount" disabled />
              </el-form-item>
              <el-form-item label="聚类数K">
                <el-slider v-model="config.k" :min="2" :max="10" show-stops />
              </el-form-item>
              <el-form-item label="遗传代数">
                <el-slider v-model="config.generations" :min="100" :max="1000" :step="100" show-stops />
              </el-form-item>
            </el-form>

            <div v-if="loading" class="progress-section">
              <el-steps :active="step" direction="vertical" size="small">
                <el-step title="数据预处理" />
                <el-step title="K-Means聚类" />
                <el-step title="遗传算法优化" />
                <el-step title="完成" />
              </el-steps>
            </div>

            <div v-if="result" class="result-section">
              <el-alert type="success" :closable="false">
                <template #title>
                  ✅ 节省 {{ result.savedDistance }}km
                </template>
              </el-alert>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import L from 'leaflet'
import 'leaflet-ant-path'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const step = ref(0)
const config = ref({ k: 5, generations: 500 })
const batchName = ref('')
const packageCount = ref('0')
const courierCount = ref('0')
const result = ref<any>(null)
const mapRef = ref()
let map: any = null
const stationId = ref(1)
const allPackages = ref<any[]>([])

const drawPackageMarkers = () => {
  const pendingPackages = allPackages.value.filter((pkg: any) => pkg.status === 'PENDING')
  pendingPackages.forEach((pkg: any) => {
    const pkgIcon = L.divIcon({
      html: '<div style="background:#3b82f6;width:8px;height:8px;border-radius:50%;border:2px solid white;box-shadow:0 2px 4px rgba(0,0,0,0.3);"></div>',
      iconSize: [8, 8]
    })
    L.marker([pkg.latitude, pkg.longitude], { icon: pkgIcon }).addTo(map).bindPopup(`${pkg.tracking_number}<br>${pkg.recipient_name}`)
  })
}

onMounted(async () => {
  batchName.value = `调度计划 ${new Date().toLocaleString('zh-CN')}`

  try {
    const [pkgRes, courierRes] = await Promise.all([
      axios.get('/api/v1/delivery/packages'),
      axios.get('/api/v1/delivery/couriers')
    ])
    allPackages.value = pkgRes.data
    const pendingCount = pkgRes.data.filter((p: any) => p.status === 'PENDING').length
    packageCount.value = pendingCount.toString()
    courierCount.value = courierRes.data.length.toString()

    map = L.map(mapRef.value).setView([31.2304, 121.4737], 12)
    L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png').addTo(map)

    const stationIcon = L.divIcon({
      html: '<div style="background:#667eea;width:20px;height:20px;border-radius:50%;border:3px solid white;box-shadow:0 4px 10px rgba(0,0,0,0.3);"></div>',
      iconSize: [20, 20]
    })
    L.marker([31.2304, 121.4737], { icon: stationIcon }).addTo(map).bindPopup('配送站')

    drawPackageMarkers()
  } catch (e) {
    console.error(e)
  }
})

const startDispatch = async () => {
  loading.value = true
  step.value = 1
  result.value = null

  try {
    ElMessage.info('正在创建调度计划...')
    const res = await axios.post('/api/v1/dispatch/plans', {
      title: batchName.value,
      station_id: stationId.value,
      algorithm_meta: config.value
    })

    step.value = 2
    ElMessage.success('计划已创建，正在计算最优路线...')

    await pollStatus(res.data.id)
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '调度失败')
    loading.value = false
    step.value = 0
  }
}

const pollStatus = async (planId: number) => {
  const interval = setInterval(async () => {
    try {
      const res = await axios.get(`/api/v1/dispatch/plans/${planId}`)
      if (res.data.status === 'READY' || res.data.status === 'COMPLETED') {
        clearInterval(interval)
        step.value = 3
        loading.value = false

        if (res.data.routes && res.data.routes.length > 0) {
          drawRoutes(res.data.routes)
          ElMessage.success('🎉 调度完成！')
        } else {
          ElMessage.error('调度失败：没有生成路线，请确保有待调度的包裹')
          step.value = 0
        }
      }
    } catch (e) {
      clearInterval(interval)
      loading.value = false
    }
  }, 1000)
}

const drawRoutes = (routes: any[]) => {
  console.log('drawRoutes called with', routes.length, 'routes')
  const colors = ['#667eea', '#48bb78', '#ed8936', '#f56565', '#9f7aea']
  let totalDistance = 0

  routes.forEach((route, idx) => {
    console.log('Processing route', idx, route)
    if (route.geo_json?.coordinates) {
      const latlngs = route.geo_json.coordinates.map((c: any) => [c[1], c[0]])
      const color = route.geo_json.color || colors[idx % colors.length]
      console.log('Drawing route with', latlngs.length, 'points, color:', color)

      try {
        if ((L as any).polyline.antPath) {
          (L as any).polyline.antPath(latlngs, {
            color,
            weight: 4,
            opacity: 0.7,
            pulseColor: '#FFFFFF',
            delay: 800
          }).addTo(map)
        } else {
          L.polyline(latlngs, {
            color,
            weight: 4,
            opacity: 0.7
          }).addTo(map)
        }
      } catch (e) {
        console.error('Error drawing route:', e)
        L.polyline(latlngs, {
          color,
          weight: 4,
          opacity: 0.7
        }).addTo(map)
      }

      if (route.geo_json.cluster_center) {
        const [centerLat, centerLon] = route.geo_json.cluster_center
        const packageCount = route.geo_json.package_count || 10
        const baseRadius = 5000
        const radius = baseRadius + (packageCount * 100)

        L.circle([centerLat, centerLon], {
          radius: radius,
          color: color,
          fillColor: color,
          fillOpacity: 0.1,
          weight: 2,
          dashArray: '5, 5'
        }).addTo(map)
      }

      totalDistance += route.geo_json.total_distance_km || 0
    }
  })

  console.log('Total distance:', totalDistance)
  result.value = {
    savedDistance: totalDistance.toFixed(1),
    savedCost: Math.round(totalDistance * 6)
  }
}

const resetDemo = async () => {
  try {
    await axios.post('/api/v1/dispatch/reset-demo')
    ElMessage.success('演示数据已重置，可以重新调度')
    result.value = null
    step.value = 0

    const [pkgRes, courierRes] = await Promise.all([
      axios.get('/api/v1/delivery/packages'),
      axios.get('/api/v1/delivery/couriers')
    ])

    allPackages.value = pkgRes.data
    const pendingCount = pkgRes.data.filter((p: any) => p.status === 'PENDING').length
    packageCount.value = pendingCount.toString()

    const availableCouriers = courierRes.data.filter((c: any) => c.status === 'AVAILABLE')
    courierCount.value = availableCouriers.length.toString()
    config.value.k = availableCouriers.length

    map.eachLayer((layer: any) => {
      if (layer instanceof L.TileLayer) return
      if (layer instanceof L.Marker && layer.options.icon?.options?.html?.includes('667eea')) return
      map.removeLayer(layer)
    })

    drawPackageMarkers()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '重置失败')
  }
}
</script>

<style scoped>
.dispatch { display: flex; flex-direction: column; gap: 20px; height: calc(100vh - 40px); }
.glass-card { background: rgba(255,255,255,0.9); backdrop-filter: blur(20px); border-radius: 16px; padding: 24px; box-shadow: 0 8px 32px rgba(0,0,0,0.1); }
.dispatch-header { display: flex; justify-content: space-between; align-items: center; }
.dispatch-header h2 { margin: 0; }
.header-actions { display: flex; gap: 12px; }
.dispatch-content { flex: 1; display: flex; flex-direction: column; min-height: 0; }
.map-panel { flex: 1; padding: 24px; display: flex; flex-direction: column; min-height: 0; }
.map-panel h3 { margin: 0 0 16px 0; }
.map-container { flex: 1; position: relative; min-height: 0; }
.map-view { width: 100%; height: 100%; border-radius: 12px; overflow: hidden; }
.config-overlay { position: absolute; top: 16px; left: 16px; width: 280px; max-height: calc(100% - 32px); overflow-y: auto; z-index: 1000; padding: 16px; background: rgba(255,255,255,0.95); }
.config-overlay h3 { margin: 0 0 12px 0; font-size: 16px; }
.progress-section { margin-top: 16px; }
.result-section { margin-top: 12px; }
</style>
