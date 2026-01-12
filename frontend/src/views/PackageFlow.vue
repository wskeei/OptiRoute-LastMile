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
            <el-option label="待分拣" value="PENDING" />
            <el-option label="已分配" value="ASSIGNED" />
            <el-option label="配送中" value="IN_TRANSIT" />
            <el-option label="已送达" value="DELIVERED" />
          </el-select>
        </div>
        <div class="header-right">
          <el-button type="primary" round :icon="Plus" @click="handleScan">扫码入库</el-button>
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

    <!-- Scan Dialog -->
    <el-dialog v-model="scanDialogVisible" title="扫码入库" width="400px">
      <el-input v-model="newTrackingNumber" placeholder="请输入快递单号" clearable />
      <template #footer>
        <el-button @click="scanDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitScan">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { Search, Plus, Download } from '@element-plus/icons-vue'

const searchQuery = ref('')
const statusFilter = ref('')
const packages = ref<any[]>([])
const scanDialogVisible = ref(false)
const newTrackingNumber = ref('')

const stats = ref([
  { label: '待分拣', value: 0, icon: 'Box', type: 'info' },
  { label: '配送中', value: 0, icon: 'Van', type: 'warning' },
  { label: '已完成', value: 0, icon: 'CircleCheck', type: 'success' },
  { label: '异常', value: 0, icon: 'Warning', type: 'danger' }
])

const fetchPackages = async () => {
  try {
    const params: any = {}
    if (statusFilter.value) params.status = statusFilter.value.toUpperCase()
    const res = await axios.get('/api/v1/delivery/packages', { params })
    packages.value = res.data
    updateStats()
  } catch (error) {
    console.error('Failed to fetch packages:', error)
  }
}

const updateStats = () => {
  const allRes = axios.get('/api/v1/stats/dashboard')
  allRes.then(res => {
    stats.value[0].value = res.data.pending_count
    stats.value[1].value = res.data.in_transit_count
    stats.value[2].value = res.data.completed_count
  })
}

const tableData = computed(() => {
  let filtered = packages.value
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    filtered = filtered.filter(p =>
      p.tracking_number?.toLowerCase().includes(q) ||
      p.recipient_name?.toLowerCase().includes(q)
    )
  }
  return filtered.map(p => ({
    trackingId: p.tracking_number,
    recipient: p.recipient_name,
    address: p.recipient_address,
    status: p.status?.toLowerCase() || 'pending',
    courier: '-'
  }))
})

const handleScan = () => {
  scanDialogVisible.value = true
}

const submitScan = async () => {
  if (!newTrackingNumber.value) return
  ElMessage.success('扫码入库功能待实现')
  scanDialogVisible.value = false
  newTrackingNumber.value = ''
}

watch(statusFilter, () => fetchPackages())

onMounted(() => fetchPackages())

const getStatusLabel = (status: string) => {
  const map: Record<string, string> = { pending: '待分拣', in_transit: '配送中', delivered: '已送达', assigned: '已分配' }
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
