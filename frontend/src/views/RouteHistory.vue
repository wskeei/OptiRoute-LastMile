<template>
  <div class="history-container">
    <div class="filter-header glass-card">
      <el-date-picker
        v-model="dateRange"
        type="daterange"
        range-separator="To"
        start-placeholder="Start"
        end-placeholder="End"
        class="modern-picker"
      />
      <el-input placeholder="搜索任务 ID" class="search-box">
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
      <el-button type="primary" round>查询历史</el-button>
    </div>

    <div class="timeline-wrap">
      <el-timeline>
        <el-timeline-item v-for="(item, idx) in history" :key="idx" :timestamp="item.time" placement="top">
          <div class="history-item glass-card">
            <div class="item-main">
              <div class="item-title">
                <h4>{{ item.title }}</h4>
                <div class="tag" :class="item.statusType">{{ item.status }}</div>
              </div>
              <div class="item-meta">
                <div class="meta-pill">📦 {{ item.packages }} 包裹</div>
                <div class="meta-pill">🚚 {{ item.couriers }} 快递员</div>
                <div class="meta-pill">⚡ {{ item.algorithm }}</div>
              </div>
              <div class="item-stats">
                <div class="stat">
                  <span class="label">优化里程</span>
                  <span class="value green">+{{ item.savedDist }}km</span>
                </div>
                <div class="stat">
                  <span class="label">节省成本</span>
                  <span class="value orange">￥{{ item.savedCost }}</span>
                </div>
              </div>
            </div>
            <div class="item-actions">
              <el-button circle :icon="View" />
              <el-button circle :icon="Download" />
              <el-button circle :icon="RefreshRight" />
            </div>
          </div>
        </el-timeline-item>
      </el-timeline>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Search, View, Download, RefreshRight } from '@element-plus/icons-vue'

const dateRange = ref('')
const history = [
  { time: '2026-01-13 09:30', title: '上午高峰批次', status: '已完成', statusType: 'success', packages: 127, couriers: 5, algorithm: 'K-Means + GA', savedDist: 32.1, savedCost: 156 },
  { time: '2026-01-12 14:15', title: '临时紧急调度', status: '已归档', statusType: 'info', packages: 89, couriers: 4, algorithm: 'K-Means + GA', savedDist: 18.7, savedCost: 89 },
]
</script>

<style scoped>
.history-container { display: flex; flex-direction: column; gap: 20px; }
.filter-header { padding: 20px; display: flex; gap: 15px; align-items: center; }
.modern-picker { width: 320px !important; }
.modern-picker :deep(.el-range-input) { background: transparent; }
.search-box { width: 200px; }

.timeline-wrap { padding: 10px 20px; }

.history-item { padding: 24px; display: flex; justify-content: space-between; align-items: center; }
.item-title { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
.item-title h4 { margin: 0; font-size: 18px; color: #2d3748; }
.tag { font-size: 11px; padding: 4px 10px; border-radius: 20px; font-weight: 700; }
.tag.success { background: rgba(72,187,120,0.1); color: #48bb78; }
.tag.info { background: rgba(102,126,234,0.1); color: #667eea; }

.item-meta { display: flex; gap: 10px; margin-bottom: 20px; }
.meta-pill { font-size: 12px; color: #718096; background: rgba(0,0,0,0.03); padding: 4px 10px; border-radius: 8px; }

.item-stats { display: flex; gap: 30px; }
.stat { display: flex; flex-direction: column; }
.stat .label { font-size: 11px; color: #a0aec0; }
.stat .value { font-size: 18px; font-weight: 800; }
.stat .value.green { color: #48bb78; }
.stat .value.orange { color: #ed8936; }

.item-actions { display: flex; gap: 10px; }
</style>