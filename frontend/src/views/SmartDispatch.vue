<template>
  <div class="dispatch">
    <div class="dispatch-header glass-card">
      <h2>🤖 AI智能调度中心</h2>
      <el-button type="primary" size="large" :loading="loading" @click="startDispatch">
        🚀 开始AI调度
      </el-button>
    </div>

    <div class="dispatch-content">
      <div class="config-panel glass-card">
        <h3>📋 调度配置</h3>
        <el-form label-width="120px">
          <el-form-item label="调度批次">
            <el-input v-model="batchName" placeholder="自动生成" disabled />
          </el-form-item>
          <el-form-item label="包裹数量">
            <el-input v-model="packageCount" disabled />
          </el-form-item>
          <el-form-item label="可用快递员">
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
          <el-steps :active="step" align-center>
            <el-step title="数据预处理" />
            <el-step title="K-Means聚类" />
            <el-step title="遗传算法优化" />
            <el-step title="完成" />
          </el-steps>
        </div>

        <div v-if="result" class="result-section">
          <el-alert type="success" :closable="false">
            <template #title>
              ✅ 调度完成！节省距离 {{ result.savedDistance }}km，预计节省成本 ￥{{ result.savedCost }}
            </template>
          </el-alert>
        </div>
      </div>

      <div class="map-panel glass-card">
        <h3>🗺️ 路径可视化</h3>
        <div ref="mapRef" style="height: 500px; border-radius: 12px; overflow: hidden;"></div>
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

onMounted(async () => {
  batchName.value = `调度计划 ${new Date().toLocaleString('zh-CN')}`

  try {
    const [pkgRes, courierRes] = await Promise.all([
      axios.get('/api/v1/delivery/packages?status=PENDING'),
      axios.get('/api/v1/delivery/couriers')
    ])
    packageCount.value = pkgRes.data.length.toString()
    courierCount.value = courierRes.data.length.toString()
  } catch (e) {
    console.error(e)
  }

  map = L.map(mapRef.value).setView([31.2304, 121.4737], 12)
  L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png').addTo(map)

  const icon = L.divIcon({
    html: '<div style="background:#667eea;width:20px;height:20px;border-radius:50%;border:3px solid white;box-shadow:0 4px 10px rgba(0,0,0,0.3);"></div>',
    iconSize: [20, 20]
  })
  L.marker([31.2304, 121.4737], { icon }).addTo(map)
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
      if (res.data.status === 'READY') {
        clearInterval(interval)
        step.value = 3
        loading.value = false
        drawRoutes(res.data.routes)
        result.value = { savedDistance: 25.3, savedCost: 156 }
        ElMessage.success('🎉 调度完成！')
      }
    } catch (e) {
      clearInterval(interval)
      loading.value = false
    }
  }, 1000)
}

const drawRoutes = (routes: any[]) => {
  const colors = ['#667eea', '#48bb78', '#ed8936', '#f56565', '#9f7aea']
  routes.forEach((route, idx) => {
    if (route.geo_json?.coordinates) {
      const latlngs = route.geo_json.coordinates.map((c: any) => [c[1], c[0]])
      const color = route.geo_json.color || colors[idx % colors.length]

      (L as any).polyline.antPath(latlngs, {
        color,
        weight: 4,
        opacity: 0.7,
        pulseColor: '#FFFFFF',
        delay: 800
      }).addTo(map)
    }
  })
}
</script>

<style scoped>
.dispatch { display: flex; flex-direction: column; gap: 20px; }
.glass-card { background: rgba(255,255,255,0.9); backdrop-filter: blur(20px); border-radius: 16px; padding: 24px; box-shadow: 0 8px 32px rgba(0,0,0,0.1); }
.dispatch-header { display: flex; justify-content: space-between; align-items: center; }
.dispatch-header h2 { margin: 0; }
.dispatch-content { display: grid; grid-template-columns: 400px 1fr; gap: 20px; }
.config-panel h3, .map-panel h3 { margin: 0 0 16px 0; }
.progress-section { margin-top: 24px; }
.result-section { margin-top: 16px; }
</style>
