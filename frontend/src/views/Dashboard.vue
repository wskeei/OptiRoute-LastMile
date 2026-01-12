<template>
  <div class="dashboard-grid">
    <!-- Hero Section -->
    <div class="hero-card glass-card">
      <div class="hero-content">
        <h1>Hello, Admin 👋</h1>
        <p>今日配送效率提升 {{ stats.efficiency_improvement }}%，系统运行平稳。</p>
        <div class="hero-stats">
          <div class="stat-pill">
            <span class="dot green"></span> 在线运力 {{ stats.online_couriers }}/{{ stats.online_couriers }}
          </div>
          <div class="stat-pill">
            <span class="dot orange"></span> 待配送 {{ stats.pending_count }}
          </div>
        </div>
      </div>
      <div class="hero-illustration">
        <!-- 简单的 CSS 几何装饰替代图片 -->
        <div class="circle c1"></div>
        <div class="circle c2"></div>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stat-card glass-card">
      <div class="icon-box blue"><el-icon><Box /></el-icon></div>
      <div class="stat-info">
        <div class="label">待配送</div>
        <div class="value">{{ stats.pending_count }}</div>
      </div>
    </div>

    <div class="stat-card glass-card">
      <div class="icon-box purple"><el-icon><Van /></el-icon></div>
      <div class="stat-info">
        <div class="label">配送中</div>
        <div class="value">{{ stats.in_transit_count }}</div>
      </div>
    </div>

    <div class="stat-card glass-card">
      <div class="icon-box green"><el-icon><CircleCheck /></el-icon></div>
      <div class="stat-info">
        <div class="label">已完成</div>
        <div class="value">{{ stats.completed_count }}</div>
      </div>
    </div>

    <!-- Main Chart -->
    <div class="chart-section glass-card">
      <div class="card-header">
        <h3>配送效率趋势</h3>
        <el-select v-model="period" size="small" style="width: 100px">
          <el-option label="本周" value="week" />
          <el-option label="本月" value="month" />
        </el-select>
      </div>
      <div ref="chartRef" class="chart-container"></div>
    </div>

    <!-- Side Lists -->
    <div class="ranking-section glass-card">
      <div class="card-header">
        <h3>🏆 运力榜单</h3>
      </div>
      <div class="ranking-list">
        <div class="rank-item" v-for="(item, index) in courierRanking" :key="index">
          <div class="rank-idx" :class="'top-'+(index+1)">{{ index + 1 }}</div>
          <el-avatar :size="32" :src="item.avatar" />
          <div class="rank-name">{{ item.name }}</div>
          <div class="rank-score">
            <el-icon><StarFilled /></el-icon> {{ item.rating }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'
import axios from 'axios'
import { Box, Van, CircleCheck, StarFilled } from '@element-plus/icons-vue'

const period = ref('week')
const chartRef = ref<HTMLElement | null>(null)

const stats = ref({ pending_count: 0, in_transit_count: 0, completed_count: 0, online_couriers: 0, efficiency_improvement: 0 })
const courierRanking = ref<any[]>([])

const fetchDashboardData = async () => {
  try {
    const [statsRes, rankingRes] = await Promise.all([
      axios.get('/api/v1/stats/dashboard'),
      axios.get('/api/v1/stats/courier-ranking')
    ])
    stats.value = statsRes.data
    courierRanking.value = rankingRes.data.map((c: any) => ({
      name: c.name,
      rating: c.delivered_count,
      avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png'
    }))
  } catch (error) {
    console.error('Failed to fetch dashboard data:', error)
  }
}

onMounted(() => {
  fetchDashboardData()

  if (chartRef.value) {
    const chart = echarts.init(chartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { top: '10%', left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: { color: '#718096' }
      },
      yAxis: {
        type: 'value',
        splitLine: { lineStyle: { type: 'dashed', color: 'rgba(0,0,0,0.05)' } }
      },
      series: [
        {
          name: 'Orders',
          type: 'line',
          smooth: true,
          itemStyle: { color: '#667eea' },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(102, 126, 234, 0.4)' },
              { offset: 1, color: 'rgba(102, 126, 234, 0)' }
            ])
          },
          data: [120, 132, 101, 134, 90, 230, 210]
        }
      ]
    })
    window.addEventListener('resize', () => chart.resize())
  }
})
</script>

<style scoped>
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: auto auto 1fr;
  gap: 20px;
  height: 100%;
}

/* Hero Section: 跨越两列 */
.hero-card {
  grid-column: 1 / 3;
  background: var(--primary-gradient) !important;
  color: white;
  padding: 30px;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.hero-content h1 {
  margin: 0 0 10px 0;
  font-size: 28px;
}
.hero-content p {
  margin: 0 0 20px 0;
  opacity: 0.9;
}

.hero-stats {
  display: flex;
  gap: 15px;
}

.stat-pill {
  background: rgba(255, 255, 255, 0.2);
  padding: 5px 15px;
  border-radius: 20px;
  font-size: 13px;
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 8px;
}
.dot.green { background: #48bb78; }
.dot.orange { background: #ed8936; }

/* 装饰圆圈 */
.circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
}
.c1 { width: 200px; height: 200px; top: -50px; right: -50px; }
.c2 { width: 100px; height: 100px; bottom: -20px; right: 80px; }

/* Stats Cards */
.stat-card {
  display: flex;
  align-items: center;
  padding: 20px;
}

.icon-box {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
  margin-right: 15px;
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}

.icon-box.blue { background: linear-gradient(135deg, #667eea, #764ba2); }
.icon-box.purple { background: linear-gradient(135deg, #b721ff, #21d4fd); }
.icon-box.green { background: linear-gradient(135deg, #0ba360, #3cba92); }

.stat-info .label { font-size: 12px; color: #718096; margin-bottom: 5px; }
.stat-info .value { font-size: 24px; font-weight: 800; color: #2d3748; }

/* Chart Section */
.chart-section {
  grid-column: 1 / 3;
  grid-row: 2 / 4;
  padding: 20px;
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.card-header h3 { margin: 0; font-size: 16px; color: #4a5568; }

.chart-container { flex: 1; min-height: 300px; }

/* Ranking Section */
.ranking-section {
  grid-column: 3 / 4;
  grid-row: 1 / 4;
  padding: 20px;
  display: flex;
  flex-direction: column;
}

.rank-item {
  display: flex;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid rgba(0,0,0,0.03);
}

.rank-idx {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  background: #edf2f7;
  color: #718096;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 12px;
  margin-right: 10px;
}

.rank-idx.top-1 { background: #ecc94b; color: white; }
.rank-idx.top-2 { background: #a0aec0; color: white; }
.rank-idx.top-3 { background: #ed8936; color: white; }

.rank-name { flex: 1; margin-left: 10px; font-weight: 600; font-size: 14px; }

.rank-score {
  display: flex;
  align-items: center;
  color: #ecc94b;
  font-weight: bold;
  font-size: 13px;
}
</style>
