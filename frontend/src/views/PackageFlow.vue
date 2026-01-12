<template>
  <div class="packages glass-card">
    <div class="header">
      <h2>📦 包裹流转中心</h2>
      <div class="actions">
        <el-input v-model="search" placeholder="搜索快递单号/收件人" style="width: 300px" clearable>
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-select v-model="statusFilter" placeholder="状态筛选" clearable style="width: 150px">
          <el-option label="待分拣" value="PENDING" />
          <el-option label="已分配" value="ASSIGNED" />
          <el-option label="配送中" value="IN_TRANSIT" />
          <el-option label="已送达" value="DELIVERED" />
        </el-select>
        <el-button type="primary">📱 扫码入库</el-button>
      </div>
    </div>
    <el-table :data="filteredPackages" style="margin-top: 20px">
      <el-table-column prop="tracking_number" label="快递单号" width="180" />
      <el-table-column prop="recipient_name" label="收件人" width="120" />
      <el-table-column prop="recipient_address" label="收件地址" show-overflow-tooltip />
      <el-table-column prop="status" label="状态" width="120">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">{{ getStatusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const packages = ref<any[]>([])
const search = ref('')
const statusFilter = ref('')

const filteredPackages = computed(() => {
  let result = packages.value
  if (search.value) {
    result = result.filter(p =>
      p.tracking_number?.includes(search.value) ||
      p.recipient_name?.includes(search.value)
    )
  }
  if (statusFilter.value) {
    result = result.filter(p => p.status === statusFilter.value)
  }
  return result
})

const getStatusType = (status: string) => {
  const map: any = { PENDING: 'info', ASSIGNED: 'warning', IN_TRANSIT: 'primary', DELIVERED: 'success' }
  return map[status] || 'info'
}

const getStatusLabel = (status: string) => {
  const map: any = { PENDING: '待分拣', ASSIGNED: '已分配', IN_TRANSIT: '配送中', DELIVERED: '已送达' }
  return map[status] || status
}

onMounted(async () => {
  try {
    const res = await axios.get('/api/v1/delivery/packages')
    packages.value = res.data
  } catch (e) {
    console.error(e)
  }
})
</script>

<style scoped>
.glass-card { background: rgba(255,255,255,0.9); backdrop-filter: blur(20px); border-radius: 16px; padding: 24px; box-shadow: 0 8px 32px rgba(0,0,0,0.1); }
.header { display: flex; justify-content: space-between; align-items: center; }
.header h2 { margin: 0; }
.actions { display: flex; gap: 12px; }
</style>
