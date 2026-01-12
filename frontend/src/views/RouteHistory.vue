<template>
  <div class="history glass-card">
    <h2>🛣️ 路线优化历史</h2>
    <el-timeline style="margin-top: 24px">
      <el-timeline-item v-for="plan in plans" :key="plan.id" :timestamp="plan.created_at">
        <el-card>
          <h4>{{ plan.title }}</h4>
          <p>状态: <el-tag :type="plan.status === 'READY' ? 'success' : 'info'">{{ plan.status }}</el-tag></p>
        </el-card>
      </el-timeline-item>
    </el-timeline>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'

const plans = ref<any[]>([])

onMounted(async () => {
  try {
    const res = await axios.get('/api/v1/dispatch/plans')
    plans.value = res.data
  } catch (e) {
    console.error(e)
  }
})
</script>

<style scoped>
.glass-card { background: rgba(255,255,255,0.9); backdrop-filter: blur(20px); border-radius: 16px; padding: 24px; box-shadow: 0 8px 32px rgba(0,0,0,0.1); }
h2 { margin: 0; }
h4 { margin: 0 0 8px 0; }
p { margin: 0; color: #718096; }
</style>
