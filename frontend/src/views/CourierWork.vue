<template>
  <div class="courier-work-container">
    <div class="layout-row">
      <!-- Left: List -->
      <div class="list-section glass-card">
        <div class="section-header">
          <h3>👥 运力实时状态</h3>
          <el-button type="primary" size="small" round :icon="Plus">添加成员</el-button>
        </div>
        
        <div class="courier-grid">
          <div v-for="c in courierList" :key="c.name" class="courier-card">
            <div class="card-top">
              <el-avatar :size="48" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" class="avatar-shadow" />
              <div class="status-badge" :class="c.status"></div>
            </div>
            <div class="card-mid">
              <div class="name">{{ c.name }}</div>
              <div class="area">{{ c.area }}</div>
            </div>
            <div class="card-bottom">
              <div class="progress-info">
                <span>进度</span>
                <span>{{ c.progress }}%</span>
              </div>
              <el-progress :percentage="c.progress" :show-text="false" :stroke-width="6" class="mini-progress" />
              <div class="task-count">{{ c.completed }}/{{ c.total }} 包裹</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right: Analysis -->
      <div class="analysis-section">
        <div class="radar-card glass-card">
          <div class="section-header">
            <h3>📊 核心效能模型</h3>
          </div>
          <div ref="radarRef" class="radar-container"></div>
        </div>

        <div class="crown-card glass-card">
          <div class="crown-glow"></div>
          <div class="crown-content">
            <div class="title">本周星级先锋 👑</div>
            <div class="performer">
              <el-avatar :size="60" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
              <div class="details">
                <div class="name">李师傅</div>
                <div class="score">98.5 <span>Score</span></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const radarRef = ref<HTMLElement | null>(null)

const courierList = [
  { name: '李师傅', area: '浦东A区', status: 'online', completed: 15, total: 20, progress: 75 },
  { name: '王师傅', area: '黄浦B区', status: 'busy', completed: 12, total: 18, progress: 66 },
  { name: '陈师傅', area: '静安C区', status: 'online', completed: 8, total: 15, progress: 53 },
  { name: '赵师傅', area: '徐汇D区', status: 'offline', completed: 0, total: 0, progress: 0 },
]

onMounted(() => {
  if (radarRef.value) {
    const chart = echarts.init(radarRef.value)
    chart.setOption({
      radar: {
        indicator: [
          { name: '速度', max: 100 },
          { name: '准时', max: 100 },
          { name: '满意度', max: 100 },
          { name: '时长', max: 100 },
          { name: '单量', max: 100 }
        ],
        splitArea: { show: false },
        axisLine: { lineStyle: { color: 'rgba(0,0,0,0.05)' } }
      },
      series: [{
        type: 'radar',
        data: [
          { value: [90, 95, 98, 80, 88], name: 'Selected', areaStyle: { color: 'rgba(102, 126, 234, 0.4)' }, itemStyle: { color: '#667eea' } },
          { value: [80, 85, 80, 70, 75], name: 'Avg', areaStyle: { color: 'rgba(0,0,0,0.05)' }, itemStyle: { color: '#cbd5e0' } }
        ]
      }]
    })
  }
})
</script>

<style scoped>
.courier-work-container { height: 100%; }
.layout-row { display: grid; grid-template-columns: 1fr 340px; gap: 20px; height: 100%; }

.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.section-header h3 { margin: 0; font-size: 18px; color: #2d3748; }

.list-section { padding: 24px; }
.courier-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 20px; }

.courier-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.03);
  display: flex;
  flex-direction: column;
  align-items: center;
  transition: transform 0.3s;
}
.courier-card:hover { transform: translateY(-5px); }

.card-top { position: relative; margin-bottom: 12px; }
.avatar-shadow { border: 3px solid white; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
.status-badge {
  position: absolute; bottom: 2px; right: 2px; width: 12px; height: 12px;
  border-radius: 50%; border: 2px solid white;
}
.status-badge.online { background: #48bb78; }
.status-badge.busy { background: #ed8936; }
.status-badge.offline { background: #a0aec0; }

.card-mid { text-align: center; margin-bottom: 15px; }
.card-mid .name { font-weight: 700; font-size: 16px; color: #2d3748; }
.card-mid .area { font-size: 12px; color: #718096; margin-top: 2px; }

.card-bottom { width: 100%; }
.progress-info { display: flex; justify-content: space-between; font-size: 11px; color: #718096; margin-bottom: 4px; }
.mini-progress { margin-bottom: 8px; }
.task-count { font-size: 12px; font-weight: 700; color: #4a5568; text-align: center; }

.analysis-section { display: flex; flex-direction: column; gap: 20px; }
.radar-card { flex: 1; padding: 20px; }
.radar-container { height: 280px; }

.crown-card {
  height: 160px; padding: 20px; position: relative; overflow: hidden;
  background: var(--primary-gradient) !important; color: white;
}
.crown-glow {
  position: absolute; top: -50%; right: -20%; width: 200px; height: 200px;
  background: rgba(255,255,255,0.2); border-radius: 50%; filter: blur(40px);
}
.crown-content { position: relative; z-index: 1; }
.crown-content .title { font-size: 14px; font-weight: 600; opacity: 0.9; margin-bottom: 15px; }
.performer { display: flex; align-items: center; gap: 15px; }
.performer .name { font-size: 20px; font-weight: 800; }
.performer .score { font-size: 24px; font-weight: 800; margin-top: 4px; }
.performer .score span { font-size: 12px; font-weight: 400; opacity: 0.8; }
</style>
