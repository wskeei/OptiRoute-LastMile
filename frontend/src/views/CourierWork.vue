<template>
  <div class="couriers page-shell">
    <section class="section-card header">
      <div>
        <span class="eyebrow">快递员数据</span>
        <h1>查看当前可参与调度的人员样本。</h1>
        <p class="header-note">这些人员会参与调度和路线回放。</p>
      </div>
      <el-button type="primary" @click="dialogVisible = true">添加快递员</el-button>
    </section>

    <section v-if="couriers.length === 0" class="section-card empty-state">
      <h2>还没有快递员样本</h2>
      <p>先添加一名快递员，调度中心才能生成路线。</p>
    </section>

    <section v-else class="section-card roster">
      <header class="roster-head">
        <h2>人员列表</h2>
        <p>当前样本按可用状态展示。</p>
      </header>

      <div class="courier-grid">
        <article v-for="courier in couriers" :key="courier.id" class="courier-card">
          <el-avatar :size="56">{{ courier.name[0] }}</el-avatar>
          <div class="courier-copy">
            <h3>{{ courier.name }}</h3>
            <p>{{ courier.phone }}</p>
          </div>
          <el-tag :type="courier.status === 'AVAILABLE' ? 'success' : 'info'">
            {{ courier.status === 'AVAILABLE' ? '在线' : '离线' }}
          </el-tag>
        </article>
      </div>
    </section>

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
  station_id: 1,
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
.couriers { display: flex; flex-direction: column; gap: 1rem; }
.header { display: flex; justify-content: space-between; align-items: flex-start; gap: 0.75rem; }
.eyebrow { display: inline-flex; margin-bottom: 0.75rem; color: #486581; font-size: 0.82rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; }
.header h1 { margin: 0; color: #102a43; font-size: clamp(1.8rem, 3vw, 2.4rem); }
.header-note { margin: 0.35rem 0 0; color: #52606d; line-height: 1.5; }
.empty-state { display: flex; flex-direction: column; gap: 0.5rem; }
.empty-state h2, .empty-state p { margin: 0; }
.roster { display: flex; flex-direction: column; gap: 0.9rem; }
.roster-head { display: flex; justify-content: space-between; align-items: baseline; gap: 0.75rem; }
.roster-head h2, .roster-head p { margin: 0; }
.roster-head p { color: #6b7f92; font-size: 0.82rem; }
.courier-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(16rem, 1fr)); gap: 0.85rem; }
.courier-card { display: flex; align-items: center; gap: 0.9rem; padding: 1rem; border-radius: 1rem; border: 1px solid rgba(24, 74, 104, 0.08); background: rgba(247, 250, 252, 0.92); }
.courier-copy { min-width: 0; flex: 1; }
.courier-card h3 { margin: 0 0 0.25rem; color: #102a43; }
.courier-card p { margin: 0; color: #6b7f92; font-size: 0.88rem; }

@media (max-width: 640px) {
  .header,
  .roster-head,
  .courier-card {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
