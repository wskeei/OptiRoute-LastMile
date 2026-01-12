<template>
  <div class="dispatch-container">
    <!-- Map Background (Fullscreen) -->
    <div id="dispatch-map" class="map-layer"></div>

    <!-- Floating Control Panel -->
    <div class="floating-panel glass-card">
      <div class="panel-header">
        <div class="panel-title">
          <el-icon><Cpu /></el-icon> 智能调度引擎
        </div>
        <div class="panel-status">
          <span class="status-dot" :class="isOptimizing ? 'processing' : 'idle'"></span>
          {{ isOptimizing ? '计算中...' : '就绪' }}
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="action-group">
        <el-button 
          type="primary" 
          size="large" 
          class="dispatch-btn"
          :loading="isOptimizing" 
          @click="startOptimization"
        >
          {{ isOptimizing ? '正在聚类...' : '立即开始调度' }}
        </el-button>
      </div>

      <!-- Config Section (Collapsible) -->
      <div class="config-section">
        <div class="config-item">
          <span class="label">配送区域 (K-Means)</span>
          <el-slider v-model="config.kValue" :min="1" :max="10" size="small" />
        </div>
        <div class="config-item">
          <span class="label">迭代深度 (GA Gen)</span>
          <el-slider v-model="config.generations" :min="100" :max="1000" :step="50" size="small" />
        </div>
      </div>

      <!-- Live Progress -->
      <transition name="fade">
        <div v-if="isOptimizing || optimizationComplete" class="progress-section">
          <div class="step-list">
             <div class="step-item" :class="{ active: activeStep >= 1 }">
               <div class="step-icon">1</div>
               <div class="step-text">数据预处理</div>
             </div>
             <div class="line" :class="{ active: activeStep >= 2 }"></div>
             <div class="step-item" :class="{ active: activeStep >= 2 }">
               <div class="step-icon">2</div>
               <div class="step-text">区域聚类</div>
             </div>
             <div class="line" :class="{ active: activeStep >= 3 }"></div>
             <div class="step-item" :class="{ active: activeStep >= 3 }">
               <div class="step-icon">3</div>
               <div class="step-text">路径优化</div>
             </div>
          </div>
        </div>
      </transition>
      
      <!-- Result Summary -->
      <transition name="slide-up">
        <div v-if="optimizationComplete" class="result-box">
          <div class="result-metric">
            <div class="val">25.3<span class="unit">km</span></div>
            <div class="lbl">节省里程</div>
          </div>
          <div class="result-metric">
            <div class="val">18<span class="unit">%</span></div>
            <div class="lbl">效率提升</div>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import L from 'leaflet'
import 'leaflet-ant-path'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { Cpu } from '@element-plus/icons-vue'

// -- State --
const isOptimizing = ref(false)
const optimizationComplete = ref(false)
const activeStep = ref(0)
const stationId = ref<number | null>(null)
const currentPlanId = ref<number | null>(null)

const config = reactive({
  kValue: 5,
  generations: 500,
  objective: 'distance'
})

// -- Map Logic --
let map: L.Map | null = null
const depotPos: [number, number] = [31.2304, 121.4737]
const markers: L.Marker[] = []
const routes: any[] = []
const clusterPolygons: L.Polygon[] = []

const initData = async () => {
  try {
    const res = await axios.post('/api/v1/utils/seed-data')
    stationId.value = res.data.station_id
  } catch (error) {
    console.error('Failed to init data:', error)
  }
}

const initMap = () => {
  map = L.map('dispatch-map', { zoomControl: false }).setView(depotPos, 13)
  
  // 使用更现代、简洁的底图 (CartoDB Voyager)
  L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
    attribution: '',
    maxZoom: 20
  }).addTo(map)
  
  // Custom Zoom Control position
  L.control.zoom({ position: 'bottomright' }).addTo(map)

  // Add Depot with Custom Icon
  const depotIcon = L.divIcon({
    className: 'custom-depot-icon',
    html: `<div style="background-color:#667eea;width:20px;height:20px;border-radius:50%;border:3px solid white;box-shadow:0 4px 10px rgba(0,0,0,0.3);"></div>`,
    iconSize: [20, 20]
  })
  L.marker(depotPos, { icon: depotIcon }).addTo(map!)
}

const startOptimization = async () => {
  if (isOptimizing.value || !stationId.value) return
  isOptimizing.value = true
  optimizationComplete.value = false
  activeStep.value = 1

  routes.forEach(r => r.remove ? r.remove() : map?.removeLayer(r))
  routes.length = 0
  markers.forEach(m => m.remove())
  markers.length = 0
  clusterPolygons.forEach(p => p.remove())
  clusterPolygons.length = 0

  try {
    const res = await axios.post('/api/v1/dispatch/plans', {
      title: `Dispatch Plan ${new Date().toLocaleTimeString()}`,
      station_id: stationId.value,
      algorithm_meta: config
    })

    currentPlanId.value = res.data.id
    activeStep.value = 2
    pollStatus()
  } catch (error) {
    ElMessage.error('调度请求失败')
    isOptimizing.value = false
  }
}

const pollStatus = async () => {
  if (!currentPlanId.value) return
  const interval = setInterval(async () => {
    try {
      const res = await axios.get(`/api/v1/dispatch/plans/${currentPlanId.value}`)
      const plan = res.data
      if (plan.status === 'READY' || plan.status === 'COMPLETED') {
        clearInterval(interval)
        handleOptimizationSuccess(plan)
      }
    } catch (e) { console.error(e) }
  }, 1000)
}

const handleOptimizationSuccess = (plan: any) => {
  activeStep.value = 3

  if (plan.routes && plan.routes.length > 0) {
    plan.routes.forEach((route: any, idx: number) => {
      if (route.geo_json && route.geo_json.coordinates) {
        const latlngs = route.geo_json.coordinates.map((c: any) => [c[1], c[0]])
        const routeColor = route.geo_json.color || '#667eea'

        // 使用 ant-path 创建动画路径
        const antPath = (L as any).polyline.antPath(latlngs, {
          color: routeColor,
          weight: 4,
          opacity: 0.7,
          pulseColor: '#FFFFFF',
          delay: 800,
          dashArray: [10, 20],
          lineCap: 'round'
        }).addTo(map!)
        routes.push(antPath)

        // 添加带序号的包裹点标记（跳过起点和终点）
        for (let i = 1; i < latlngs.length - 1; i++) {
          const numberIcon = L.divIcon({
            className: 'package-number-marker',
            html: `<div style="background-color:${routeColor};color:white;width:24px;height:24px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:bold;border:2px solid white;box-shadow:0 2px 6px rgba(0,0,0,0.3);">${i}</div>`,
            iconSize: [24, 24]
          })
          const marker = L.marker(latlngs[i], { icon: numberIcon }).addTo(map!)

          // 添加 tooltip 显示包裹信息
          marker.bindTooltip(`包裹 #${i}<br>路线: ${idx + 1}`, {
            direction: 'top',
            offset: [0, -12]
          })
          markers.push(marker)
        }

        // 绘制聚类区域边界（使用凸包近似）
        if (route.geo_json.cluster_center && latlngs.length > 3) {
          const clusterCenter = [route.geo_json.cluster_center[0], route.geo_json.cluster_center[1]]
          const packagePoints = latlngs.slice(1, -1) // 排除起点和终点

          // 简单的凸包近似：按角度排序点
          const sortedPoints = packagePoints.sort((a: any, b: any) => {
            const angleA = Math.atan2(a[0] - clusterCenter[0], a[1] - clusterCenter[1])
            const angleB = Math.atan2(b[0] - clusterCenter[0], b[1] - clusterCenter[1])
            return angleA - angleB
          })

          const polygon = L.polygon(sortedPoints, {
            color: routeColor,
            weight: 2,
            opacity: 0.4,
            fillColor: routeColor,
            fillOpacity: 0.1,
            dashArray: '5, 5'
          }).addTo(map!)

          polygon.bindTooltip(`聚类 ${idx + 1}<br>包裹数: ${route.geo_json.package_count}<br>距离: ${route.geo_json.total_distance_km}km`, {
            sticky: true
          })
          clusterPolygons.push(polygon)
        }
      }
    })
  }

  // 模拟稍微延迟一下结束动画
  setTimeout(() => {
    isOptimizing.value = false
    optimizationComplete.value = true
    ElMessage.success('智能调度完成')
  }, 800)
}

onMounted(() => {
  initMap()
  initData()
})
</script>

<style scoped>
.dispatch-container {
  position: relative;
  height: 100%;
  width: 100%;
  border-radius: var(--border-radius-lg);
  overflow: hidden;
  box-shadow: var(--glass-shadow);
}

.map-layer {
  width: 100%;
  height: 100%;
  z-index: 1;
}

/* 悬浮面板 */
.floating-panel {
  position: absolute;
  top: 20px;
  left: 20px;
  width: 320px;
  background: rgba(255, 255, 255, 0.9) !important;
  backdrop-filter: blur(20px);
  padding: 20px;
  z-index: 1000;
  border-radius: 20px !important;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-title {
  font-weight: 800;
  font-size: 16px;
  color: #2d3748;
  display: flex;
  align-items: center;
  gap: 8px;
}

.panel-status {
  font-size: 12px;
  color: #718096;
  display: flex;
  align-items: center;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  margin-right: 5px;
}
.status-dot.idle { background: #48bb78; }
.status-dot.processing { background: #ed8936; animation: pulse 1s infinite; }

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

.dispatch-btn {
  width: 100%;
  height: 44px;
  font-weight: 600;
  letter-spacing: 0.5px;
  border-radius: 12px;
}

.config-item {
  margin-bottom: 10px;
}
.config-item .label {
  font-size: 12px;
  color: #a0aec0;
  display: block;
  margin-bottom: 5px;
}

/* 进度条样式 */
.step-list {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
}

.step-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  z-index: 2;
}

.step-icon {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #edf2f7;
  color: #cbd5e0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
  transition: all 0.3s;
}

.step-item.active .step-icon {
  background: var(--primary-color);
  color: white;
  box-shadow: 0 0 10px rgba(102, 126, 234, 0.4);
}

.step-text {
  font-size: 10px;
  color: #a0aec0;
  margin-top: 4px;
}

.line {
  flex: 1;
  height: 2px;
  background: #edf2f7;
  margin: 0 5px 15px 5px;
  position: relative;
  top: -8px;
}
.line.active { background: var(--primary-color); }

/* 结果摘要 */
.result-box {
  background: linear-gradient(135deg, #f6f8fd, #f1f4f9);
  border-radius: 12px;
  padding: 15px;
  display: flex;
  justify-content: space-around;
  border: 1px solid rgba(0,0,0,0.03);
}

.result-metric { text-align: center; }
.result-metric .val { font-size: 20px; font-weight: 800; color: #2d3748; }
.result-metric .unit { font-size: 12px; color: #a0aec0; margin-left: 2px; }
.result-metric .lbl { font-size: 11px; color: #718096; margin-top: 2px; }

/* 动画 */
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.slide-up-enter-active { transition: all 0.4s ease-out; }
.slide-up-enter-from { opacity: 0; transform: translateY(10px); }
</style>
