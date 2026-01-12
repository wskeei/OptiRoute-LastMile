<template>
  <div class="package-flow-container">
    <!-- Header Stats -->
    <div class="stats-row">
      <div v-for="(stat, index) in stats" :key="index" class="glass-card stat-item">
        <div class="stat-icon" :class="stat.type">
          <el-icon><component :is="stat.icon" /></el-icon>
        </div>
        <div class="stat-info">
          <div class="val">{{ stat.value }}</div>
          <div class="lbl">{{ stat.label }}</div>
        </div>
      </div>
    </div>

    <!-- Filter & Table Card -->
    <div class="table-section glass-card">
      <div class="table-header">
        <div class="header-left">
          <el-input
            v-model="searchQuery"
            placeholder="搜索快递单号 / 收件人"
            class="search-input"
            clearable
          >
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
          <el-select v-model="statusFilter" placeholder="包裹状态" class="status-select" clearable>
            <el-option label="待分拣" value="pending" />
            <el-option label="配送中" value="delivering" />
            <el-option label="已送达" value="completed" />
          </el-select>
        </div>
        <div class="header-right">
          <el-button type="primary" round :icon="Plus">扫码入库</el-button>
          <el-button round :icon="Download">导出</el-button>
        </div>
      </div>

      <el-table :data="tableData" class="modern-table">
        <el-table-column prop="trackingId" label="快递单号" width="160">
          <template #default="scope">
            <span class="tracking-code">{{ scope.row.trackingId }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="recipient" label="收件人" width="120" />
        <el-table-column prop="address" label="收件地址" min-width="200" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="120" align="center">
          <template #default="scope">
            <div class="status-pill" :class="scope.row.status">
              {{ getStatusLabel(scope.row.status) }}
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="courier" label="快递员" width="120">
          <template #default="scope">
            <div class="courier-cell">
              <el-avatar :size="24" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
              <span>{{ scope.row.courier }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" align="right">
          <template #default>
            <el-button link type="primary">查看</el-button>
            <el-divider direction="vertical" />
            <el-button link>编辑</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-box">
        <el-pagination background layout="prev, pager, next" :total="127" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Search, Plus, Download } from '@element-plus/icons-vue'

const searchQuery = ref('')
const statusFilter = ref('')

const stats = [
  { label: '待分拣', value: 45, icon: 'Box', type: 'info' },
  { label: '配送中', value: 87, icon: 'Van', type: 'warning' },
  { label: '已完成', value: 342, icon: 'CircleCheck', type: 'success' },
  { label: '异常', value: 3, icon: 'Warning', type: 'danger' }
]

const tableData = [
  { trackingId: 'SF1000293841', recipient: '张三', address: '上海市浦东新区张江高科园区A栋101', status: 'delivering', courier: '李师傅' },
  { trackingId: 'YT2938471923', recipient: '李四', address: '上海市黄浦区南京东路888号', status: 'pending', courier: '-' },
  { trackingId: 'JD9283746152', recipient: '王五', address: '上海市静安区静安寺街道123号', status: 'completed', courier: '陈师傅' },
  { trackingId: 'ZT1234567890', recipient: '赵六', address: '上海市徐汇区港汇恒隆广场', status: 'issue', courier: '王师傅' },
]

const getStatusLabel = (status: string) => {
  const map: Record<string, string> = { pending: '待分拣', delivering: '配送中', completed: '已送达', issue: '异常' }
  return map[status] || '未知'
}
</script>

<style scoped>
.package-flow-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.stat-item {
  display: flex;
  align-items: center;
  padding: 20px;
}

.stat-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  margin-right: 15px;
}

.stat-icon.info { background: rgba(102, 126, 234, 0.1); color: #667eea; }
.stat-icon.warning { background: rgba(237, 137, 54, 0.1); color: #ed8936; }
.stat-icon.success { background: rgba(72, 187, 120, 0.1); color: #48bb78; }
.stat-icon.danger { background: rgba(245, 101, 101, 0.1); color: #f56565; }

.stat-info .val { font-size: 22px; font-weight: 800; color: #2d3748; }
.stat-info .lbl { font-size: 12px; color: #718096; }

.table-section {
  padding: 24px;
  display: flex;
  flex-direction: column;
}

.table-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 24px;
}

.header-left {
  display: flex;
  gap: 12px;
}

.search-input { width: 240px; }
.search-input :deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.5);
  border-radius: 12px;
  box-shadow: none !important;
  border: 1px solid rgba(0,0,0,0.05);
}

.status-select :deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.5);
  border-radius: 12px;
  box-shadow: none !important;
  border: 1px solid rgba(0,0,0,0.05);
}

.tracking-code {
  font-family: 'Monaco', monospace;
  font-weight: 600;
  color: #667eea;
}

.status-pill {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.status-pill.pending { background: rgba(113, 128, 150, 0.1); color: #718096; }
.status-pill.delivering { background: rgba(237, 137, 54, 0.1); color: #ed8936; }
.status-pill.completed { background: rgba(72, 187, 120, 0.1); color: #48bb78; }
.status-pill.issue { background: rgba(245, 101, 101, 0.1); color: #f56565; }

.courier-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pagination-box {
  margin-top: 24px;
  display: flex;
  justify-content: center;
}
</style>
