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
        <el-button type="primary" @click="dialogVisible = true">📱 扫码入库</el-button>
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

    <el-dialog v-model="dialogVisible" title="包裹入库" width="40%">
      <el-form :model="form" label-width="100px">
        <el-form-item label="快递单号">
          <el-input v-model="form.tracking_number" placeholder="扫描或输入单号" />
          <el-button type="text" @click="generateTracking">📦 生成单号</el-button>
        </el-form-item>
        <el-form-item label="收件人">
          <el-input v-model="form.recipient_name" />
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="form.recipient_phone" />
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="form.recipient_address" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="重量(kg)">
              <el-input-number v-model="form.weight" :precision="1" :step="0.1" :min="0.1" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="体积(m³)">
              <el-input-number v-model="form.volume" :precision="2" :step="0.01" :min="0.01" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleAdd">入库</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const packages = ref<any[]>([])
const search = ref('')
const statusFilter = ref('')
const dialogVisible = ref(false)

const form = reactive({
  tracking_number: '',
  recipient_name: '',
  recipient_phone: '',
  recipient_address: '',
  weight: 1.0,
  volume: 0.1,
  latitude: 31.2304, // Default to Shanghai center
  longitude: 121.4737
})

const generateTracking = () => {
  form.tracking_number = 'SF' + Date.now().toString().slice(-10)
}

const fetchPackages = async () => {
  try {
    const res = await axios.get('/api/v1/delivery/packages')
    packages.value = res.data
  } catch (e) {
    console.error(e)
  }
}

const handleAdd = async () => {
  try {
    // Generate random lat/lon slightly around center if not provided (simulation)
    form.latitude = 31.2304 + (Math.random() - 0.5) * 0.1
    form.longitude = 121.4737 + (Math.random() - 0.5) * 0.1
    
    await axios.post('/api/v1/delivery/packages', form)
    ElMessage.success('包裹入库成功')
    dialogVisible.value = false
    fetchPackages()
  } catch (e) {
    ElMessage.error('入库失败')
  }
}

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

onMounted(() => {
  fetchPackages()
})
</script>

<style scoped>
.glass-card { background: rgba(255,255,255,0.9); backdrop-filter: blur(20px); border-radius: 16px; padding: 24px; box-shadow: 0 8px 32px rgba(0,0,0,0.1); }
.header { display: flex; justify-content: space-between; align-items: center; }
.header h2 { margin: 0; }
.actions { display: flex; gap: 12px; }
</style>
