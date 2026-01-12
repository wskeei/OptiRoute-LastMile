<template>
  <div class="monitor-container">
    <div id="monitor-map" class="map-view"></div>

    <!-- Floating Panels -->
    <div class="floating-controls left glass-card">
      <div class="panel-header">🎛️ 图层管理</div>
      <div class="control-list">
        <el-checkbox v-model="layers.couriers">快递员轨迹</el-checkbox>
        <el-checkbox v-model="layers.packages">实时包裹分布</el-checkbox>
        <el-checkbox v-model="layers.stations">配送站网络</el-checkbox>
      </div>
    </div>

    <div class="floating-controls right glass-card">
      <div class="panel-header">📍 动态监控</div>
      <div class="monitor-list">
        <div v-for="c in onlineCouriers" :key="c.id" class="monitor-item">
          <div class="m-top">
            <span class="m-name">{{ c.name }}</span>
            <span class="m-badge" :class="c.status"></span>
          </div>
          <div class="m-pos">{{ c.lastPos }}</div>
          <div class="m-speed">速度: 24 km/h</div>
        </div>
      </div>
    </div>

    <div class="floating-alert glass-card" v-if="hasAlert">
      <el-icon color="#f56565"><WarningFilled /></el-icon>
      <span>检测到 2 名快递员偏离预定路线</span>
      <el-button type="danger" link>立即处理</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import L from 'leaflet'
import { WarningFilled } from '@element-plus/icons-vue'

const layers = reactive({ couriers: true, packages: true, stations: true })
const onlineCouriers = [
  { id: 1, name: '李师傅', lastPos: '浦东大道123号', status: 'online' },
  { id: 2, name: '王师傅', lastPos: '南京东路456号', status: 'busy' },
]
const hasAlert = ref(true)

onMounted(() => {
  const map = L.map('monitor-map', { zoomControl: false }).setView([31.2304, 121.4737], 13)
  L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png').addTo(map)
  L.control.zoom({ position: 'bottomright' }).addTo(map)
  
  // Custom Markers
  const customIcon = L.divIcon({
    className: 'c-marker',
    html: '<div style="background:#667eea;width:12px;height:12px;border-radius:50%;border:2px solid white;box-shadow:0 0 10px rgba(102,126,234,0.5);"></div>'
  })
  L.marker([31.235, 121.48], { icon: customIcon }).addTo(map).bindPopup('李师傅')
  L.marker([31.225, 121.46], { icon: customIcon }).addTo(map).bindPopup('王师傅')
})
</script>

<style scoped>
.monitor-container { position: relative; height: 100%; width: 100%; border-radius: 24px; overflow: hidden; }
.map-view { width: 100%; height: 100%; z-index: 1; }

.floating-controls {
  position: absolute; top: 20px; z-index: 1000; width: 200px; padding: 16px;
  background: rgba(255,255,255,0.85) !important;
}
.floating-controls.left { left: 20px; }
.floating-controls.right { right: 20px; width: 240px; }

.panel-header { font-weight: 700; font-size: 14px; margin-bottom: 12px; color: #2d3748; }
.control-list { display: flex; flex-direction: column; gap: 8px; }

.monitor-list { display: flex; flex-direction: column; gap: 12px; }
.monitor-item { padding: 10px; background: rgba(0,0,0,0.03); border-radius: 12px; }
.m-top { display: flex; justify-content: space-between; align-items: center; }
.m-name { font-weight: 600; font-size: 13px; }
.m-badge { width: 8px; height: 8px; border-radius: 50%; }
.m-badge.online { background: #48bb78; }
.m-badge.busy { background: #ed8936; }
.m-pos { font-size: 11px; color: #718096; margin-top: 4px; }
.m-speed { font-size: 10px; color: #a0aec0; margin-top: 2px; }

.floating-alert {
  position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%);
  z-index: 1000; padding: 12px 24px; display: flex; align-items: center; gap: 12px;
  background: rgba(255,255,255,0.95) !important; font-size: 14px; font-weight: 600;
  border-left: 4px solid #f56565 !important;
}
</style>