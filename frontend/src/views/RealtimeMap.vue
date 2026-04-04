<template>
  <div class="realtime-map">
    <div class="control-panel glass-card">
      <div class="panel-copy">
        <h2>路线监控</h2>
        <p>查看最近一次已完成调度的路线与配送进度。</p>
      </div>
      <div class="controls">
        <el-button type="primary" @click="nextStep" :disabled="!canStep">
          下一步 ({{ currentStep }}/{{ totalSteps }})
        </el-button>
        <el-button @click="resetSimulation">重置</el-button>
      </div>
    </div>

    <el-alert v-if="statusMessage" type="info" :closable="false" show-icon :title="statusMessage">
      如需看到路线结果，请先前往调度中心重置演示数据并启动一次调度。
    </el-alert>

    <div class="map-container glass-card">
      <div ref="mapRef" style="height: calc(100vh - 200px); border-radius: 12px; overflow: hidden;"></div>
    </div>

    <div class="info-panel glass-card">
      <h3>配送进度</h3>
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
import { sortPlansByNewest } from '../lib/analytics'

const mapRef = ref()
let map: any = null
const routes = ref<any[]>([])
const courierStatus = ref<any[]>([])
const currentStep = ref(0)
const statusMessage = ref('')
let courierMarkers: any[] = [] // Non-reactive to prevent Leaflet proxy issues
type GeoJsonCoord = [number, number]

const stationCoord: L.LatLngTuple = [31.2304, 121.4737]
const colors = ['#667eea', '#48bb78', '#ed8936', '#f56565', '#9f7aea']

const toLatLng = (coord: GeoJsonCoord): L.LatLngTuple => [coord[1], coord[0]]

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
      statusMessage.value = '还没有可用于监控的调度计划'
      ElMessage.warning('暂无调度计划')
      return
    }

    const sortedPlans = sortPlansByNewest(planRes.data)
    const latestPlan = sortedPlans.find((p: any) => p.status === 'READY')
    
    if (!latestPlan || !latestPlan.routes || latestPlan.routes.length === 0) {
      statusMessage.value = '最近一次调度还没有可展示的路线结果'
      ElMessage.warning('最新计划没有路线数据')
      return
    }

    statusMessage.value = ''
    routes.value = latestPlan.routes
    initializeSimulation()
  } catch (e) {
    console.error(e)
    statusMessage.value = '加载路线结果失败'
    ElMessage.error('加载调度计划失败')
  }
}

const drawRoutesAndPackages = () => {
  routes.value.forEach((route, idx) => {
    const color = route.geo_json?.color || colors[idx % colors.length]

    if (route.geo_json?.coordinates) {
      const latlngs = route.geo_json.coordinates.map((c: GeoJsonCoord) => toLatLng(c))
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
      // The coordinates array is [Depot, Pkg1, Pkg2, ..., Depot]
      // packages_ordered index i matches coordinates index i+1
      const pkgs = route.geo_json.packages_ordered || []
      
      route.geo_json.coordinates.slice(1, -1).forEach((coord: any, pkgIdx: number) => {
        const icon = L.divIcon({
          html: `<div style="background:${color};color:white;width:24px;height:24px;border-radius:50%;border:2px solid white;box-shadow:0 2px 6px rgba(0,0,0,0.4);display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:bold;">${pkgIdx + 1}</div>`,
          iconSize: [24, 24]
        })
        const marker = L.marker(toLatLng(coord as GeoJsonCoord), { icon }).addTo(map)
        
        // Add detailed popup if data available
        if (pkgs[pkgIdx]) {
           const p = pkgs[pkgIdx]
           marker.bindPopup(`
             <div style="font-size:13px;">
               <b>${pkgIdx + 1}. ${p.recipient_name || '收件人'}</b><br>
               <span style="color:#666">单号: ${p.tracking_number || '-'}</span><br>
               <span style="color:#666">重量: ${p.weight || 1}kg</span><br>
               <span style="color:#666">${p.address || ''}</span>
             </div>
           `)
        }
      })
    }
  })
}

const drawCouriers = () => {
  // Initialize markers if not present
  if (courierMarkers.length === 0) {
     courierStatus.value.forEach(courier => {
        const icon = L.divIcon({
          className: 'custom-courier-icon',
          html: `
            <div class="courier-marker-inner" style="background-color: ${courier.color}">
              <span class="icon">🚚</span>
              <span class="name">${courier.name}</span>
            </div>
          `,
          iconSize: [0, 0],
          iconAnchor: [0, 0]
        })
        const marker = L.marker(courier.currentPos, { icon }).addTo(map)
        courierMarkers.push(marker)
     })
  }

  // Update positions and popups for all markers
  courierStatus.value.forEach((courier, idx) => {
    const marker = courierMarkers[idx]
    if (!marker) return

    // Update position smoothly
    marker.setLatLng(courier.currentPos)

    // Calculate dynamic info
    let currentWeight = 0
    if (courier.route.geo_json?.packages_ordered) {
         const allPkgs = courier.route.geo_json.packages_ordered
         const deliveredCount = courier.delivered
         for (let i = deliveredCount; i < allPkgs.length; i++) {
             currentWeight += (allPkgs[i].weight || 0)
         }
    } else {
        currentWeight = (courier.total - courier.delivered) * 1.5
    }

    // Update popup content (keeps it open if already open)
    const popupContent = `
        <div style="text-align:center;">
            <b>${courier.name}</b><br>
            <span style="color:#667eea;font-weight:bold;">当前载重: ${currentWeight.toFixed(1)}kg</span><br>
            <span style="color:#999;font-size:12px;">最大承载: ${courier.maxCapacity}kg</span><br>
            <span style="font-size:12px;color:#999">剩余包裹: ${courier.total - courier.delivered}个</span>
        </div>
    `
    
    // If popup is bound, set content. If not (first time), bind it.
    if (marker.getPopup()) {
        marker.setPopupContent(popupContent)
    } else {
        marker.bindPopup(popupContent)
    }
  })
}

const initializeSimulation = () => {
  courierStatus.value = routes.value.map((route, idx) => ({
    id: route.courier_id || idx,
    name: route.courier?.name || `快递员${idx + 1}`,
    color: route.geo_json?.color || colors[idx % colors.length],
    total: route.geo_json?.package_count || 0,
    delivered: 0,
    currentPos: [...stationCoord],
    maxCapacity: route.courier?.max_capacity || 50,
    route: route
  }))

  drawRoutesAndPackages()
  drawCouriers()
}

const nextStep = () => {
  if (!canStep.value) return

  currentStep.value++

  courierStatus.value.forEach(courier => {
    // Check if courier has packages left to deliver
    if (courier.delivered < courier.total) {
      const coords = courier.route.geo_json?.coordinates
      // Ensure coords exist and index is valid
      // Valid path: Depot(0) -> Pkg1(1) ... PkgN(N) -> Depot(N+1)
      // Moving to: delivered + 1
      if (coords && coords.length > courier.delivered + 1) {
        const nextCoord = coords[courier.delivered + 1] as GeoJsonCoord
        // GeoJSON is [lon, lat], Leaflet needs [lat, lon]
        courier.currentPos = toLatLng(nextCoord)
        courier.delivered++
      } else {
        console.warn(`Missing coordinates for courier ${courier.name} at step ${courier.delivered}`)
        // Force increment to avoid stuck loop logic, but position won't update
        courier.delivered++ 
      }
    }
  })

  drawCouriers()

  if (!canStep.value) {
    ElMessage.success('所有包裹配送完成')
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
.panel-copy h2 { margin: 0 0 4px; }
.panel-copy p { margin: 0; color: #52606d; font-size: 14px; }
.controls { display: flex; gap: 12px; }
.info-panel h3 { margin: 0 0 16px 0; }
.courier-list { display: flex; flex-direction: column; gap: 12px; }
.courier-item { padding: 12px; background: rgba(102, 126, 234, 0.05); border-radius: 8px; }
.courier-name { font-weight: bold; font-size: 16px; margin-bottom: 4px; }
.courier-progress { font-size: 14px; color: #718096; }

:deep(.custom-courier-icon) {
  background: none;
  border: none;
}

:deep(.courier-marker-inner) {
  position: absolute;
  top: 0;
  left: 0;
  transform: translate(-50%, -50%); /* Centers the marker exactly on the coordinate */
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border-radius: 12px;
  color: white;
  font-weight: bold;
  font-size: 12px;
  white-space: nowrap;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  border: 2px solid white;
  transition: transform 0.2s; /* Smooth visual effects if needed */
}

:deep(.courier-marker-inner:hover) {
  z-index: 1000;
  transform: translate(-50%, -50%) scale(1.1);
}

@media (max-width: 640px) {
  .control-panel {
    flex-direction: column;
    align-items: flex-start;
  }

  .controls {
    width: 100%;
    flex-wrap: wrap;
  }
}
</style>
