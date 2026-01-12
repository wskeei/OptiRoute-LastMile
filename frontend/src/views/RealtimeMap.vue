<template>
  <div class="realtime-map">
    <div class="control-panel glass-card">
      <h2>🗺️ 实时监控地图</h2>
      <div class="controls">
        <el-button type="primary" @click="nextStep" :disabled="!canStep">
          ▶️ 下一步 ({{ currentStep }}/{{ totalSteps }})
        </el-button>
        <el-button @click="resetSimulation">🔄 重置</el-button>
      </div>
    </div>

    <div class="map-container glass-card">
      <div ref="mapRef" style="height: calc(100vh - 200px); border-radius: 12px; overflow: hidden;"></div>
    </div>

    <div class="info-panel glass-card">
      <h3>📊 配送进度</h3>
      <div class="courier-list">
        <div v-for="courier in courierStatus" :key="courier.id" class="courier-item">
          <div class="courier-name" :style="{ color: courier.color }">
            {{ courier.name }}
          </div>
          <div class="courier-progress">
            已送达: {{ courier.delivered }}/{{ courier.total }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import L from 'leaflet'
import 'leaflet-ant-path'
import { ElMessage } from 'element-plus'

const mapRef = ref()
let map: any = null
const routes = ref<any[]>([])
const courierStatus = ref<any[]>([])
const currentStep = ref(0)
const courierMarkers = ref<any[]>([])
const stationCoord = [31.2304, 121.4737]
const colors = ['#667eea', '#48bb78', '#ed8936', '#f56565', '#9f7aea']

const totalSteps = computed(() => {
  return Math.max(...courierStatus.value.map(c => c.total), 0)
})

const canStep = computed(() => {
  return currentStep.value < totalSteps.value
})

onMounted(async () => {
  map = L.map(mapRef.value).setView(stationCoord, 12)
  L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png').addTo(map)

  const stationIcon = L.divIcon({
    html: '<div style="background:#667eea;width:24px;height:24px;border-radius:50%;border:3px solid white;box-shadow:0 4px 10px rgba(0,0,0,0.3);"></div>',
    iconSize: [24, 24]
  })
  L.marker(stationCoord, { icon: stationIcon }).addTo(map).bindPopup('配送站')

  await loadLatestDispatch()
})

const loadLatestDispatch = async () => {
  try {
    const planRes = await axios.get('/api/v1/dispatch/plans')
    if (planRes.data.length === 0) {
      ElMessage.warning('暂无调度计划')
      return
    }

    const latestPlan = planRes.data.find((p: any) => p.status === 'READY')
    if (!latestPlan || !latestPlan.routes || latestPlan.routes.length === 0) {
      ElMessage.warning('最新计划没有路线数据')
      return
    }

    routes.value = latestPlan.routes
    initializeSimulation()
  } catch (e) {
    console.error(e)
    ElMessage.error('加载调度计划失败')
  }
}

const initializeSimulation = () => {
  courierStatus.value = routes.value.map((route, idx) => ({
    id: route.courier_id || idx,
    name: route.courier?.name || `快递员${idx + 1}`,
    color: route.geo_json?.color || colors[idx % colors.length],
    total: route.geo_json?.package_count || 0,
    delivered: 0,
    currentPos: [...stationCoord],
    route: route
  }))

  drawRoutesAndPackages()
  drawCouriers()
}

const drawRoutesAndPackages = () => {
  routes.value.forEach((route, idx) => {
    const color = route.geo_json?.color || colors[idx % colors.length]

    if (route.geo_json?.coordinates) {
      const latlngs = route.geo_json.coordinates.map((c: any) => [c[1], c[0]])
      L.polyline(latlngs, { color, weight: 3, opacity: 0.4, dashArray: '5, 5' }).addTo(map)
    }

    if (route.geo_json?.cluster_center) {
      const [centerLat, centerLon] = route.geo_json.cluster_center
      const packageCount = route.geo_json.package_count || 10
      const radius = 5000 + (packageCount * 100)
      L.circle([centerLat, centerLon], {
        radius, color, fillColor: color, fillOpacity: 0.05, weight: 2, dashArray: '5, 5'
      }).addTo(map)
    }

    if (route.geo_json?.coordinates && route.geo_json.coordinates.length > 2) {
      route.geo_json.coordinates.slice(1, -1).forEach((coord: any, pkgIdx: number) => {
        const icon = L.divIcon({
          html: `<div style="background:${color};color:white;width:24px;height:24px;border-radius:50%;border:2px solid white;box-shadow:0 2px 6px rgba(0,0,0,0.4);display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:bold;">${pkgIdx + 1}</div>`,
          iconSize: [24, 24]
        })
        L.marker([coord[1], coord[0]], { icon }).addTo(map)
      })
    }
  })
}

const drawCouriers = () => {
  courierMarkers.value.forEach(m => map.removeLayer(m))
  courierMarkers.value = []

  courierStatus.value.forEach(courier => {
    const icon = L.divIcon({
      html: `<div style="background:${courier.color};color:white;padding:4px 8px;border-radius:12px;border:2px solid white;box-shadow:0 2px 8px rgba(0,0,0,0.4);font-size:12px;font-weight:bold;white-space:nowrap;">🚚 ${courier.name}</div>`,
      className: 'courier-marker',
      iconAnchor: [40, 15]
    })
    const marker = L.marker(courier.currentPos, { icon }).addTo(map)
    courierMarkers.value.push(marker)
  })
}

const nextStep = () => {
  if (!canStep.value) return

  currentStep.value++

  courierStatus.value.forEach(courier => {
    if (courier.delivered < courier.total) {
      const coords = courier.route.geo_json?.coordinates
      if (coords && coords.length > courier.delivered + 1) {
        const nextCoord = coords[courier.delivered + 1]
        courier.currentPos = [nextCoord[1], nextCoord[0]]
        courier.delivered++
      }
    }
  })

  drawCouriers()

  if (!canStep.value) {
    ElMessage.success('🎉 所有包裹配送完成！')
  }
}

const resetSimulation = () => {
  currentStep.value = 0
  courierStatus.value.forEach(courier => {
    courier.delivered = 0
    courier.currentPos = [...stationCoord]
  })
  drawCouriers()
  ElMessage.info('已重置到初始状态')
}
</script>

<style scoped>
.realtime-map { display: flex; flex-direction: column; gap: 20px; }
.glass-card { background: rgba(255,255,255,0.9); backdrop-filter: blur(20px); border-radius: 16px; padding: 24px; box-shadow: 0 8px 32px rgba(0,0,0,0.1); }
.control-panel { display: flex; justify-content: space-between; align-items: center; }
.control-panel h2 { margin: 0; }
.controls { display: flex; gap: 12px; }
.info-panel h3 { margin: 0 0 16px 0; }
.courier-list { display: flex; flex-direction: column; gap: 12px; }
.courier-item { padding: 12px; background: rgba(102, 126, 234, 0.05); border-radius: 8px; }
.courier-name { font-weight: bold; font-size: 16px; margin-bottom: 4px; }
.courier-progress { font-size: 14px; color: #718096; }
</style>
