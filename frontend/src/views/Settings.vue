<template>
  <div class="settings page-shell">
    <section class="page-hero">
      <div>
        <span class="eyebrow">系统说明</span>
        <h1>说明当前演示如何运行。</h1>
        <p class="page-summary">这里只保留会影响判断的规则和维护动作。</p>
      </div>
    </section>

    <section class="settings-grid">
      <article class="section-card">
        <header class="section-head">
          <div>
            <h2>当前数据概览</h2>
            <p>来自接口的实际样本数量。</p>
          </div>
          <el-button @click="loadStats">刷新数据</el-button>
        </header>

        <div class="stats-grid">
          <div class="stat-item">
            <span>包裹总数</span>
            <strong>{{ stats.totalPackages }}</strong>
          </div>
          <div class="stat-item">
            <span>快递员总数</span>
            <strong>{{ stats.totalCouriers }}</strong>
          </div>
          <div class="stat-item">
            <span>配送站点数</span>
            <strong>{{ stats.totalStations }}</strong>
          </div>
          <div class="stat-item">
            <span>历史计划数</span>
            <strong>{{ stats.totalPlans }}</strong>
          </div>
        </div>
      </article>

      <article class="section-card">
        <header class="section-head">
          <div>
            <h2>数据维护</h2>
            <p>保留明确、可解释的重置动作。</p>
          </div>
        </header>

        <div class="action-list">
          <div class="action-item">
            <div>
              <strong>重新初始化包裹样本</strong>
              <p>清空当前包裹并重新生成演示样本。</p>
            </div>
            <el-button type="warning" @click="reinitPackages">重新初始化</el-button>
          </div>

          <div class="action-item">
            <div>
              <strong>清空调度历史</strong>
              <p>删除历史计划与路线，并重置包裹和快递员状态。</p>
            </div>
            <el-button type="danger" @click="clearHistory">清空历史</el-button>
          </div>
        </div>
      </article>

    </section>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

const stats = ref({ totalPackages: 0, totalCouriers: 0, totalStations: 1, totalPlans: 0 })

onMounted(() => {
  loadStats()
})

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
  } catch (error) {
    console.error(error)
  }
}

const reinitPackages = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要重新初始化包裹样本吗？这会清空当前包裹并重新生成演示数据。',
      '确认操作',
      {
        confirmButtonText: '重新初始化',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    ElMessage.info('正在重新初始化包裹样本...')
    await axios.post('/api/v1/delivery/packages/reinit')
    await loadStats()
    ElMessage.success('包裹样本已重新初始化')
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '初始化失败')
    }
  }
}

const clearHistory = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有调度历史吗？此操作不可恢复。',
      '确认操作',
      {
        confirmButtonText: '清空历史',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    ElMessage.info('正在清空调度历史...')
    await axios.delete('/api/v1/dispatch/plans/all')
    await loadStats()
    ElMessage.success('调度历史已清空')
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '清空失败')
    }
  }
}
</script>

<style scoped>
.settings {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.page-hero h1 {
  margin: 0 0 0.5rem;
  color: #102a43;
  font-size: clamp(1.8rem, 3vw, 2.4rem);
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

.page-summary {
  margin: 0;
  max-width: 42rem;
  color: #52606d;
  line-height: 1.6;
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
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

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.75rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  padding: 1rem;
  border-radius: 1rem;
  background: rgba(224, 232, 240, 0.45);
}

.stat-item span {
  color: #486581;
  font-size: 0.88rem;
}

.stat-item strong {
  color: #102a43;
  font-size: 1.85rem;
}

.action-list {
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
}

.action-item {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem;
  border-radius: 1rem;
  background: rgba(247, 250, 252, 0.92);
  border: 1px solid rgba(24, 74, 104, 0.08);
}

.action-item strong {
  display: block;
  margin-bottom: 0.35rem;
  color: #102a43;
}

.action-item p {
  margin: 0;
  color: #52606d;
  line-height: 1.5;
}

@media (max-width: 900px) {
  .settings-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .action-item {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
