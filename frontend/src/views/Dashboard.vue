<template>
  <div class="dashboard">
    <div class="welcome-card glass-card">
      <h1>👋 欢迎回来，管理员</h1>
      <p>{{ new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' }) }}</p>
    </div>

    <div class="quick-actions glass-card">
      <h3>🚀 快速操作</h3>
      <div class="action-buttons">
        <el-button type="primary" @click="$router.push('/dispatch')">📦 新建调度</el-button>
        <el-button @click="$router.push('/packages')">📋 扫描入库</el-button>
        <el-button @click="$router.push('/monitor')">👀 实时监控</el-button>
        <el-button>📊 生成报告</el-button>
      </div>
    </div>

    <div class="stats-grid">
      <div class="stat-card glass-card">
        <div class="stat-icon blue">📦</div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.pending }}</div>
          <div class="stat-label">待配送</div>
        </div>
      </div>
      <div class="stat-card glass-card">
        <div class="stat-icon orange">🚚</div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.inTransit }}</div>
          <div class="stat-label">配送中</div>
        </div>
      </div>
      <div class="stat-card glass-card">
        <div class="stat-icon green">✅</div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.completed }}</div>
          <div class="stat-label">已完成</div>
        </div>
      </div>
      <div class="stat-card glass-card">
        <div class="stat-icon purple">👥</div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.couriers }}</div>
          <div class="stat-label">在线快递员</div>
        </div>
      </div>
    </div>

    <div class="chart-section glass-card">
      <h3>📈 配送效率趋势</h3>
      <div ref="chartRef" style="height: 300px"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'

const stats = ref({ pending: 0, inTransit: 0, completed: 0, couriers: 0 })
const chartRef = ref()

onMounted(async () => {
  try {
    const res = await axios.get('/api/v1/stats/dashboard')
    stats.value = {
      pending: res.data.pending_count,
      inTransit: res.data.in_transit_count,
      completed: res.data.completed_count,
      couriers: res.data.online_couriers
    }
  } catch (e) {
    console.error(e)
  }

  if (chartRef.value) {
    const chart = echarts.init(chartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'] },
      yAxis: { type: 'value' },
      series: [{ data: [120, 132, 101, 134, 90, 230, 210], type: 'line', smooth: true, areaStyle: {} }]
    })
  }
})
</script>

<style scoped>
.dashboard { display: flex; flex-direction: column; gap: 20px; }
.glass-card { background: rgba(255,255,255,0.9); backdrop-filter: blur(20px); border-radius: 16px; padding: 24px; box-shadow: 0 8px 32px rgba(0,0,0,0.1); }
.welcome-card h1 { margin: 0 0 8px 0; font-size: 28px; color: #2d3748; }
.welcome-card p { margin: 0; color: #718096; }
.quick-actions h3 { margin: 0 0 16px 0; }
.action-buttons { display: flex; gap: 12px; flex-wrap: wrap; }
.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }
.stat-card { display: flex; align-items: center; gap: 16px; }
.stat-icon { width: 56px; height: 56px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 28px; }
.stat-icon.blue { background: linear-gradient(135deg, #667eea, #764ba2); }
.stat-icon.orange { background: linear-gradient(135deg, #f093fb, #f5576c); }
.stat-icon.green { background: linear-gradient(135deg, #4facfe, #00f2fe); }
.stat-icon.purple { background: linear-gradient(135deg, #a8edea, #fed6e3); }
.stat-value { font-size: 32px; font-weight: bold; color: #2d3748; }
.stat-label { font-size: 14px; color: #718096; }
.chart-section h3 { margin: 0 0 16px 0; }
</style>
