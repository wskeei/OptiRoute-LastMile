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
        <p>点击任意卡片可查看该快递员的详细信息。</p>
      </header>

      <div class="courier-grid">
        <button
          v-for="courier in couriers"
          :key="courier.id"
          type="button"
          class="courier-card"
          @click="openCourierDetails(courier)"
        >
          <div class="courier-top">
            <el-avatar :size="56">{{ courier.name[0] }}</el-avatar>
            <div class="courier-copy">
              <div class="courier-title">
                <h3>{{ courier.name }}</h3>
                <span class="courier-id">#{{ courier.id }}</span>
              </div>
              <p>{{ courier.phone }}</p>
            </div>
            <el-tag :type="statusTagType(courier.status)">
              {{ statusLabel(courier.status) }}
            </el-tag>
          </div>

          <div class="courier-metrics">
            <div class="metric-chip">
              <span>最大载重</span>
              <strong>{{ courier.max_capacity }} kg</strong>
            </div>
            <div class="metric-chip">
              <span>所属站点</span>
              <strong>{{ stationLabel(courier) }}</strong>
            </div>
          </div>

          <div class="courier-footer">
            <span>点击查看详情</span>
            <span class="footer-arrow">查看</span>
          </div>
        </button>
      </div>
    </section>

    <el-drawer v-model="drawerVisible" title="快递员详情" direction="rtl" :size="drawerSize">
      <div v-if="selectedCourier" class="drawer-body">
        <section class="detail-panel hero-panel">
          <div class="detail-identity">
            <el-avatar :size="64">{{ selectedCourier.name[0] }}</el-avatar>
            <div>
              <p class="detail-eyebrow">快递员档案</p>
              <h2>{{ selectedCourier.name }}</h2>
              <p class="detail-subtitle">{{ stationLabel(selectedCourier) }}</p>
            </div>
          </div>
          <el-tag :type="statusTagType(selectedCourier.status)">
            {{ statusLabel(selectedCourier.status) }}
          </el-tag>
        </section>

        <section class="detail-panel">
          <h3>基础信息</h3>
          <div class="detail-grid">
            <div class="detail-item">
              <span>姓名</span>
              <strong>{{ selectedCourier.name }}</strong>
            </div>
            <div class="detail-item">
              <span>手机号</span>
              <strong>{{ selectedCourier.phone }}</strong>
            </div>
            <div class="detail-item">
              <span>工号</span>
              <strong>#{{ selectedCourier.id }}</strong>
            </div>
            <div class="detail-item">
              <span>所属站点</span>
              <strong>{{ stationLabel(selectedCourier) }}</strong>
            </div>
          </div>
        </section>

        <section class="detail-panel">
          <h3>运力信息</h3>
          <div class="detail-grid">
            <div class="detail-item">
              <span>最大载重</span>
              <strong>{{ selectedCourier.max_capacity }} kg</strong>
            </div>
            <div class="detail-item">
              <span>当前载重</span>
              <strong>接口暂未提供</strong>
            </div>
            <div class="detail-item">
              <span>调度状态</span>
              <strong>{{ statusLabel(selectedCourier.status) }}</strong>
            </div>
            <div class="detail-item">
              <span>站点编号</span>
              <strong>{{ selectedCourier.station_id }}</strong>
            </div>
          </div>
        </section>
      </div>
    </el-drawer>

    <el-dialog v-model="dialogVisible" title="添加快递员" :width="dialogWidth">
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
import { ref, onMounted, onBeforeUnmount, reactive } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

interface CourierItem {
  id: number
  name: string
  phone: string
  status: string
  max_capacity: number
  station_id: number
}

const couriers = ref<CourierItem[]>([])
const dialogVisible = ref(false)
const dialogWidth = ref('30rem')
const drawerVisible = ref(false)
const drawerSize = ref('26rem')
const selectedCourier = ref<CourierItem | null>(null)
const currentStationId = ref<number | null>(null)
const currentStationName = ref('')
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

const loadCurrentStation = async () => {
  try {
    const stationRes = await axios.get('/api/v1/delivery/stations/current')
    currentStationId.value = stationRes.data.id
    currentStationName.value = stationRes.data.name || ''
    form.station_id = stationRes.data.id
  } catch (e) {
    console.error(e)
  }
}

const handleAdd = async () => {
  try {
    if (currentStationId.value) {
      form.station_id = currentStationId.value
    }
    await axios.post('/api/v1/delivery/couriers', form)
    ElMessage.success('添加成功')
    dialogVisible.value = false
    fetchCouriers()
  } catch (e) {
    ElMessage.error('添加失败')
  }
}

const stationLabel = (courier: CourierItem) => {
  if (courier.station_id === currentStationId.value && currentStationName.value) {
    return currentStationName.value
  }

  return `站点 ${courier.station_id}`
}

const statusLabel = (status: string) => (status === 'AVAILABLE' ? '在线' : '离线')
const statusTagType = (status: string) => (status === 'AVAILABLE' ? 'success' : 'info')

const openCourierDetails = (courier: CourierItem) => {
  selectedCourier.value = courier
  drawerVisible.value = true
}

const syncDialogWidth = () => {
  if (typeof window === 'undefined') return
  dialogWidth.value = window.innerWidth <= 640 ? '90vw' : '30rem'
  drawerSize.value = window.innerWidth <= 640 ? '92vw' : '28rem'
}

onMounted(() => {
  syncDialogWidth()
  window.addEventListener('resize', syncDialogWidth)
  loadCurrentStation()
  fetchCouriers()
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', syncDialogWidth)
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
.courier-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(18rem, 1fr)); gap: 0.95rem; }
.courier-card {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem;
  border-radius: 1.15rem;
  border: 1px solid rgba(24, 74, 104, 0.08);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(247, 250, 252, 0.96)),
    rgba(247, 250, 252, 0.92);
  text-align: left;
  cursor: pointer;
  transition:
    transform 0.18s ease,
    box-shadow 0.18s ease,
    border-color 0.18s ease;
}
.courier-card:hover {
  transform: translateY(-2px);
  border-color: rgba(24, 74, 104, 0.18);
  box-shadow: 0 16px 30px rgba(15, 23, 42, 0.08);
}
.courier-top { display: flex; align-items: flex-start; gap: 0.9rem; }
.courier-copy { min-width: 0; flex: 1; }
.courier-title { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.3rem; }
.courier-card h3 { margin: 0; color: #102a43; }
.courier-id { color: #829ab1; font-size: 0.82rem; }
.courier-card p { margin: 0; color: #6b7f92; font-size: 0.9rem; }
.courier-metrics { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0.75rem; }
.metric-chip {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 0.8rem 0.85rem;
  border-radius: 0.95rem;
  background: rgba(241, 245, 249, 0.92);
  border: 1px solid rgba(24, 74, 104, 0.08);
}
.metric-chip span { color: #486581; font-size: 0.8rem; }
.metric-chip strong { color: #102a43; font-size: 0.94rem; line-height: 1.4; }
.courier-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #486581;
  font-size: 0.84rem;
  font-weight: 600;
}
.footer-arrow {
  color: #184a68;
}
.drawer-body { display: flex; flex-direction: column; gap: 1rem; }
.detail-panel {
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
  padding: 1rem;
  border-radius: 1rem;
  background: rgba(247, 250, 252, 0.92);
  border: 1px solid rgba(24, 74, 104, 0.08);
}
.hero-panel {
  flex-direction: row;
  justify-content: space-between;
  align-items: flex-start;
}
.detail-identity { display: flex; align-items: center; gap: 0.85rem; }
.detail-eyebrow {
  margin: 0 0 0.25rem;
  color: #486581;
  font-size: 0.78rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}
.detail-panel h2,
.detail-panel h3,
.detail-panel p { margin: 0; }
.detail-panel h2,
.detail-panel h3 { color: #102a43; }
.detail-subtitle { color: #52606d; line-height: 1.5; }
.detail-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0.75rem; }
.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 0.85rem 0.9rem;
  border-radius: 0.9rem;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(24, 74, 104, 0.08);
}
.detail-item span { color: #486581; font-size: 0.8rem; }
.detail-item strong { color: #102a43; font-size: 0.95rem; line-height: 1.4; }

@media (max-width: 640px) {
  .header,
  .roster-head,
  .courier-top,
  .hero-panel {
    flex-direction: column;
    align-items: flex-start;
  }

  .courier-metrics,
  .detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>
