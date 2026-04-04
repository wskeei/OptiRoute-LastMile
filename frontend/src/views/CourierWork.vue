<template>
  <div class="couriers glass-card">
    <div class="header">
      <h2>👥 快递员工作台</h2>
      <el-button type="primary" @click="dialogVisible = true">➕ 添加快递员</el-button>
    </div>
    <div class="courier-grid">
      <div v-for="courier in couriers" :key="courier.id" class="courier-card">
        <el-avatar :size="60">{{ courier.name[0] }}</el-avatar>
        <h3>{{ courier.name }}</h3>
        <p>{{ courier.phone }}</p>
        <el-tag :type="courier.status === 'AVAILABLE' ? 'success' : 'info'">
          {{ courier.status === 'AVAILABLE' ? '在线' : '离线' }}
        </el-tag>
      </div>
    </div>
    <el-dialog v-model="dialogVisible" title="添加快递员" width="30%">
      <el-form :model="form" label-width="80px">
        <el-form-item label="姓名">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item label="最大载重">
          <el-input-number v-model="form.max_capacity" :min="1" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleAdd">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const couriers = ref<any[]>([])
const dialogVisible = ref(false)
const form = reactive({
  name: '',
  phone: '',
  max_capacity: 50,
  station_id: 1, // Default station
  status: 'AVAILABLE'
})

const fetchCouriers = async () => {
  try {
    const res = await axios.get('/api/v1/delivery/couriers')
    couriers.value = res.data
  } catch (e) {
    console.error(e)
  }
}

const handleAdd = async () => {
  try {
    await axios.post('/api/v1/delivery/couriers', form)
    ElMessage.success('添加成功')
    dialogVisible.value = false
    fetchCouriers()
  } catch (e) {
    ElMessage.error('添加失败')
  }
}

onMounted(() => {
  fetchCouriers()
})
</script>

<style scoped>
.glass-card { background: rgba(255,255,255,0.9); backdrop-filter: blur(20px); border-radius: 16px; padding: 24px; box-shadow: 0 8px 32px rgba(0,0,0,0.1); }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.header h2 { margin: 0; }
.courier-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 20px; }
.courier-card { background: white; border-radius: 12px; padding: 20px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.courier-card h3 { margin: 12px 0 4px 0; }
.courier-card p { margin: 0 0 12px 0; color: #718096; font-size: 14px; }
</style>
