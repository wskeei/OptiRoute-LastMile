<template>
  <div class="settings">
    <div class="glass-card header">
      <h2>⚙️ 系统设置</h2>
    </div>

    <div class="settings-grid">
      <div class="glass-card">
        <h3>🧠 算法默认参数</h3>
        <div class="param-section">
          <div class="param-group">
            <div class="param-label">K-Means 聚类数 K</div>
            <el-slider v-model="config.k" :min="2" :max="10" show-stops />
            <div class="param-value">{{ config.k }}</div>
          </div>
          <div class="param-group">
            <div class="param-label">遗传算法代数</div>
            <el-slider v-model="config.generations" :min="100" :max="1000" :step="100" show-stops />
            <div class="param-value">{{ config.generations }}</div>
          </div>
          <div class="param-group">
            <div class="param-label">种群大小</div>
            <el-slider v-model="config.populationSize" :min="50" :max="200" :step="10" show-stops />
            <div class="param-value">{{ config.populationSize }}</div>
          </div>
        </div>
        <div class="action-buttons">
          <el-button type="primary" @click="saveConfig">💾 保存配置</el-button>
          <el-button @click="resetConfig">🔄 恢复默认</el-button>
        </div>
      </div>

      <div class="glass-card">
        <h3>📊 系统数据统计</h3>
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-label">数据库包裹总数</div>
            <div class="stat-value">{{ stats.totalPackages }}</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">快递员总数</div>
            <div class="stat-value">{{ stats.totalCouriers }}</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">配送站点数</div>
            <div class="stat-value">{{ stats.totalStations }}</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">历史调度次数</div>
            <div class="stat-value">{{ stats.totalPlans }}</div>
          </div>
        </div>
        <el-button @click="loadStats" style="margin-top: 16px">🔄 刷新统计</el-button>
      </div>

      <div class="glass-card">
        <h3>🗄️ 数据管理</h3>
        <div class="data-actions">
          <div class="action-item">
            <div class="action-desc">
              <div class="action-title">重新初始化包裹数据</div>
              <div class="action-subtitle">清空现有包裹，重新生成300个上海地点包裹</div>
            </div>
            <el-button type="warning" @click="reinitPackages">🔄 重新初始化</el-button>
          </div>
          <div class="action-item">
            <div class="action-desc">
              <div class="action-title">清空调度历史</div>
              <div class="action-subtitle">删除所有历史调度计划和路线数据</div>
            </div>
            <el-button type="danger" @click="clearHistory">🗑️ 清空历史</el-button>
          </div>
        </div>
      </div>

      <div class="glass-card">
        <h3>ℹ️ 系统信息</h3>
        <div class="info-list">
          <div class="info-item">
            <span class="info-label">系统版本</span>
            <span class="info-value">v1.0.0</span>
          </div>
          <div class="info-item">
            <span class="info-label">后端框架</span>
            <span class="info-value">FastAPI + Python 3.11</span>
          </div>
          <div class="info-item">
            <span class="info-label">前端框架</span>
            <span class="info-value">Vue 3 + TypeScript</span>
          </div>
          <div class="info-item">
            <span class="info-label">算法实现</span>
            <span class="info-value">K-Means + 遗传算法</span>
          </div>
          <div class="info-item">
            <span class="info-label">数据库</span>
            <span class="info-value">SQLite</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

const config = ref({ k: 5, generations: 500, populationSize: 100 })
const stats = ref({ totalPackages: 0, totalCouriers: 0, totalStations: 1, totalPlans: 0 })

onMounted(() => {
  const saved = localStorage.getItem('algorithmConfig')
  if (saved) config.value = JSON.parse(saved)
  loadStats()
})

const saveConfig = () => {
  localStorage.setItem('algorithmConfig', JSON.stringify(config.value))
  ElMessage.success('算法默认参数已保存')
}

const resetConfig = () => {
  config.value = { k: 5, generations: 500, populationSize: 100 }
  ElMessage.success('已恢复默认配置')
}

const loadStats = async () => {
  try {
    const [packagesRes, couriersRes, plansRes] = await Promise.all([
      axios.get('/api/v1/delivery/packages'),
      axios.get('/api/v1/delivery/couriers'),
      axios.get('/api/v1/dispatch/plans')
    ])
    stats.value.totalPackages = packagesRes.data.length
    stats.value.totalCouriers = couriersRes.data.length
    stats.value.totalPlans = plansRes.data.length
  } catch (e) {
    console.error(e)
  }
}

const reinitPackages = async () => {
  try {
    await ElMessageBox.confirm('确定要重新初始化包裹数据吗？这将清空现有包裹并重新生成300个包裹。', '确认操作', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    ElMessage.info('正在重新初始化包裹数据...')
    await axios.post('/api/v1/delivery/packages/reinit')
    await loadStats()
    ElMessage.success('包裹数据已重新初始化')
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error(e.response?.data?.detail || '初始化失败')
    }
  }
}

const clearHistory = async () => {
  try {
    await ElMessageBox.confirm('确定要清空所有调度历史吗？此操作不可恢复。', '确认操作', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    ElMessage.info('正在清空调度历史...')
    await axios.delete('/api/v1/dispatch/plans/all')
    await loadStats()
    ElMessage.success('调度历史已清空')
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error(e.response?.data?.detail || '清空失败')
    }
  }
}
</script>

<style scoped>
.settings { display: flex; flex-direction: column; gap: 20px; }
.glass-card { background: rgba(255,255,255,0.9); backdrop-filter: blur(20px); border-radius: 16px; padding: 24px; box-shadow: 0 8px 32px rgba(0,0,0,0.1); }
h2, h3 { margin: 0; margin-bottom: 20px; }

.header { display: flex; justify-content: space-between; align-items: center; }

.settings-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }

.param-section { display: flex; flex-direction: column; gap: 20px; margin-bottom: 20px; }
.param-group { display: flex; flex-direction: column; gap: 8px; }
.param-label { font-size: 14px; color: #718096; font-weight: 500; }
.param-value { text-align: center; font-size: 18px; font-weight: bold; color: #667eea; margin-top: 4px; }

.action-buttons { display: flex; gap: 12px; }

.stats-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin-bottom: 16px; }
.stat-item { text-align: center; padding: 16px; background: rgba(102, 126, 234, 0.05); border-radius: 8px; }
.stat-label { font-size: 13px; color: #718096; margin-bottom: 8px; }
.stat-value { font-size: 28px; font-weight: bold; color: #667eea; }

.data-actions { display: flex; flex-direction: column; gap: 16px; }
.action-item { display: flex; justify-content: space-between; align-items: center; padding: 16px; background: rgba(102, 126, 234, 0.03); border-radius: 8px; }
.action-desc { flex: 1; }
.action-title { font-size: 15px; font-weight: 500; color: #2d3748; margin-bottom: 4px; }
.action-subtitle { font-size: 13px; color: #718096; }

.info-list { display: flex; flex-direction: column; gap: 12px; }
.info-item { display: flex; justify-content: space-between; padding: 12px; background: rgba(102, 126, 234, 0.03); border-radius: 6px; }
.info-label { font-size: 14px; color: #718096; }
.info-value { font-size: 14px; font-weight: 500; color: #2d3748; }
</style>
