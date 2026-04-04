<template>
  <div class="packages page-shell">
    <section class="section-card header">
      <div class="header-text">
        <span class="eyebrow">包裹数据</span>
        <h1>查看和补充演示包裹。</h1>
        <p class="header-note">演示样本仅用于流程演练。</p>
      </div>
      <div class="actions">
        <div class="action-field">
          <el-input v-model="search" placeholder="搜索快递单号/收件人" clearable>
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </div>
        <div class="action-field">
          <el-select v-model="statusFilter" placeholder="状态筛选" clearable>
            <el-option label="待分拣" value="PENDING" />
            <el-option label="已分配" value="ASSIGNED" />
            <el-option label="配送中" value="IN_TRANSIT" />
            <el-option label="已送达" value="DELIVERED" />
          </el-select>
        </div>
        <div class="action-field action-button">
          <el-button type="primary" @click="dialogVisible = true">录入示例包裹</el-button>
        </div>
      </div>
    </section>

    <section class="section-card table-card">
      <header class="table-head">
        <h2>包裹列表</h2>
        <p class="table-note">当前显示演示录入和后端记录。</p>
      </header>

      <el-table :data="filteredPackages">
        <el-table-column prop="tracking_number" label="快递单号" width="180" />
        <el-table-column prop="recipient_name" label="收件人" width="120" />
        <el-table-column prop="recipient_address" label="收件地址" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </section>

    <el-dialog
      v-model="dialogVisible"
      title="演示包裹录入"
      class="package-dialog"
      :width="dialogWidth"
      destroy-on-close
    >
      <el-form :model="form" label-width="100px">
        <el-form-item label="快递单号">
          <el-input v-model="form.tracking_number" placeholder="扫描或输入单号" />
          <el-button type="text" @click="generateTracking">生成单号</el-button>
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
          <span class="dialog-hint">提交后会自动补齐演示坐标。</span>
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleAdd">入库</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, reactive } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'

const packages = ref<any[]>([])
const search = ref('')
const statusFilter = ref('')
const dialogVisible = ref(false)
const dialogWidth = ref('480px')

const form = reactive({
  tracking_number: '',
  recipient_name: '',
  recipient_phone: '',
  recipient_address: '',
  weight: 1.0,
  volume: 0.1,
  latitude: 31.2304,
  longitude: 121.4737
})

const generateTracking = () => {
  form.tracking_number = 'SF' + Date.now().toString().slice(-10)
}

const adjustDialogWidth = () => {
  if (typeof window === 'undefined') return
  const available = window.innerWidth
  dialogWidth.value = available < 640 ? `${Math.floor(available * 0.9)}px` : '480px'
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
    result = result.filter(
      (item) =>
        item.tracking_number?.includes(search.value) || item.recipient_name?.includes(search.value)
    )
  }
  if (statusFilter.value) {
    result = result.filter((item) => item.status === statusFilter.value)
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
  adjustDialogWidth()
  window.addEventListener('resize', adjustDialogWidth)
  fetchPackages()
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', adjustDialogWidth)
})
</script>

<style scoped>
.packages {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 0.75rem;
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

.header h1 {
  margin: 0;
  color: #102a43;
  font-size: clamp(1.8rem, 3vw, 2.4rem);
}

.header-text {
  max-width: 32rem;
}

.header-note {
  margin: 0.35rem 0 0;
  color: #52606d;
  line-height: 1.5;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  align-items: center;
}

.action-field {
  flex: 1 1 220px;
  min-width: 200px;
}

.action-field.action-button {
  flex: 0 0 auto;
  align-self: center;
}

.action-field > * {
  width: 100%;
}

.table-card {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.table-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 0.75rem;
}

.table-head h2 {
  margin: 0;
  color: #102a43;
  font-size: 1.1rem;
}

.table-note {
  margin: 0;
  color: #6b7f92;
  font-size: 0.82rem;
}

.package-dialog .el-dialog {
  max-width: 480px;
}

.dialog-footer {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
}

.dialog-hint {
  color: #6b7f92;
  font-size: 0.82rem;
}

@media (max-width: 640px) {
  .header {
    flex-direction: column;
  }

  .table-head,
  .dialog-footer {
    flex-direction: column;
    align-items: flex-start;
  }

  .action-field {
    min-width: auto;
  }
}
</style>
