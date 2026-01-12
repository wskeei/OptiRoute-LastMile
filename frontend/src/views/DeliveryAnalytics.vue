<template>
  <div class="analytics-container">
    <div class="kpi-grid">
      <div v-for="kpi in kpis" :key="kpi.label" class="glass-card kpi-item">
        <div class="kpi-main">
          <div class="val">{{ kpi.value }}</div>
          <div class="lbl">{{ kpi.label }}</div>
        </div>
        <div class="kpi-trend" :class="kpi.trend >= 0 ? 'up' : 'down'">
          {{ kpi.trend >= 0 ? '+' : '' }}{{ kpi.trend }}%
        </div>
      </div>
    </div>

    <div class="charts-row">
      <div class="glass-card chart-box">
        <div class="chart-header">🧠 算法优化效果 (里程节省)</div>
        <div ref="algoChartRef" class="chart-content"></div>
      </div>
      <div class="glass-card chart-box">
        <div class="chart-header">📊 配送量预测 (未来 7 天)</div>
        <div ref="trendChartRef" class="chart-content"></div>
      </div>
    </div>

    <div class="glass-card full-chart">
      <div class="chart-header">🏢 站点负载热力图</div>
      <div ref="heatChartRef" class="chart-content"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import * as echarts from 'echarts'

const kpis = [
  { label: '平均时效', value: '28m', trend: -12.5 },
  { label: '优化里程', value: '1,240km', trend: 8.2 },
  { label: '满载率', value: '92.4%', trend: 3.1 },
  { label: '客户满意度', value: '4.92', trend: 0.5 },
]

const algoChartRef = ref<HTMLElement | null>(null)
const trendChartRef = ref<HTMLElement | null>(null)
const heatChartRef = ref<HTMLElement | null>(null)

onMounted(() => {
  const commonOptions = {
    grid: { top: 20, left: 40, right: 20, bottom: 40 },
    xAxis: { type: 'category', axisLine: { show: false }, axisTick: { show: false } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: 'rgba(0,0,0,0.03)' } } }
  }

  if (algoChartRef.value) {
    const chart = echarts.init(algoChartRef.value)
    chart.setOption({
      ...commonOptions,
      xAxis: { ...commonOptions.xAxis, data: ['W1', 'W2', 'W3', 'W4', 'W5'] },
      series: [{ data: [820, 932, 901, 934, 1290], type: 'line', smooth: true, itemStyle: { color: '#667eea' } }]
    })
  }
  if (trendChartRef.value) {
    const chart = echarts.init(trendChartRef.value)
    chart.setOption({
      ...commonOptions,
      xAxis: { ...commonOptions.xAxis, data: ['1.14', '1.15', '1.16', '1.17', '1.18'] },
      series: [{ data: [120, 200, 150, 80, 70], type: 'bar', itemStyle: { color: '#764ba2' } }]
    })
  }
  if (heatChartRef.value) {
    const chart = echarts.init(heatChartRef.value)
    chart.setOption({
      tooltip: { position: 'top' },
      grid: { height: '70%', top: '10%' },
      xAxis: { type: 'category', data: ['08:00', '10:00', '12:00', '14:00', '16:00', '18:00'], splitArea: { show: true } },
      yAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'], splitArea: { show: true } },
      visualMap: { min: 0, max: 100, calculable: true, orient: 'horizontal', left: 'center', bottom: '5%', inRange: { color: ['#ebedf0', '#667eea'] } },
      series: [{
        name: 'Load', type: 'heatmap',
        data: [[0,0,5],[0,1,1],[0,2,0],[0,3,0],[0,4,0],[1,0,3],[1,1,70],[1,2,90],[1,3,10],[1,4,0]],
        label: { show: false }
      }]
    })
  }
})
</script>

<style scoped>
.analytics-container { display: flex; flex-direction: column; gap: 20px; }
.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }

.kpi-item { padding: 24px; display: flex; justify-content: space-between; align-items: flex-end; }
.kpi-main .val { font-size: 28px; font-weight: 800; color: #2d3748; }
.kpi-main .lbl { font-size: 13px; color: #718096; margin-top: 4px; }
.kpi-trend { font-size: 13px; font-weight: 700; padding: 4px 8px; border-radius: 8px; }
.kpi-trend.up { background: rgba(72,187,120,0.1); color: #48bb78; }
.kpi-trend.down { background: rgba(245,101,101,0.1); color: #f56565; }

.charts-row { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.chart-box { padding: 24px; height: 320px; }
.full-chart { padding: 24px; height: 300px; }

.chart-header { font-weight: 700; font-size: 16px; margin-bottom: 20px; color: #4a5568; }
.chart-content { height: calc(100% - 40px); }
</style>