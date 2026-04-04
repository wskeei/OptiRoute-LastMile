<template>
  <div class="page-shell">
    <div class="auth-card">
      <div class="card-header">
        <p class="eyebrow">配送调度访问</p>
        <h1>登录</h1>
        <p class="description">使用账号进入调度台。</p>
      </div>

      <el-form :model="form" class="auth-form">
        <el-form-item label="用户名" label-width="90px">
          <el-input
            v-model="form.username"
            size="large"
            :prefix-icon="User"
            clearable
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-form-item label="密码" label-width="90px">
          <el-input
            v-model="form.password"
            type="password"
            size="large"
            :prefix-icon="Lock"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-button
          type="primary"
          size="large"
          :loading="loading"
          @click="handleLogin"
          class="auth-button"
        >
          <span v-if="!loading">登录</span>
          <span v-else>登录中...</span>
        </el-button>
      </el-form>

      <div v-if="status.message" class="status-zone">
        <el-alert
          :title="status.message"
          :type="status.type || 'info'"
          show-icon
          :closable="false"
          class="status-alert"
        />
      </div>

      <div class="footer">
        <span>还没有账号？</span>
        <router-link to="/register" class="link">前往注册</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { User, Lock } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  username: '',
  password: ''
})

const loading = ref(false)
const status = ref<{ type: '' | 'success' | 'error'; message: string }>({
  type: '',
  message: ''
})

const clearStatus = () => {
  status.value = { type: '', message: '' }
}

const setStatus = (type: 'success' | 'error', message: string) => {
  status.value = { type, message }
}

const handleLogin = async () => {
  clearStatus()
  if (!form.value.username || !form.value.password) {
    setStatus('error', '请输入用户名和密码')
    return
  }

  loading.value = true
  try {
    await authStore.login(form.value.username, form.value.password)
    setStatus('success', '登录成功，正在引导您进入调度')
    await router.push('/dispatch')
  } catch (error: any) {
    setStatus(
      'error',
      error.response?.data?.detail || '登录失败，请检查用户名与密码是否正确'
    )
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.page-shell {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #eef1f6;
  padding: 40px 16px;
}

.auth-card {
  width: min(420px, calc(100% - 32px));
  padding: clamp(24px, 5vw, 36px);
  background: var(--auth-surface);
  border-radius: 16px;
  box-shadow: var(--auth-shadow);
  border: 1px solid var(--auth-border);
}

.card-header {
  text-align: center;
  margin-bottom: 24px;
}

.eyebrow {
  margin: 0;
  font-size: 12px;
  letter-spacing: 0.2em;
  color: #475569;
  text-transform: uppercase;
}

h1 {
  margin: 8px 0 4px;
  font-size: 28px;
  font-weight: 600;
  color: #0f172a;
}

.description {
  margin: 0;
  font-size: 14px;
  color: #475569;
  line-height: 1.5;
}

.auth-form {
  margin-bottom: 16px;
}

.el-form-item {
  margin-bottom: 18px;
}

:deep(.el-input__wrapper) {
  border-radius: 10px;
  border-color: #cbd5f5;
}

:deep(.el-input__wrapper:hover) {
  border-color: #94a3b8;
}

:deep(.el-input__wrapper.is-focus) {
  border-color: #475569;
  box-shadow: 0 0 0 2px rgba(71, 85, 105, 0.12);
}

.auth-button {
  width: 100%;
  height: 48px;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 600;
  background: #0f172a;
  border: none;
}

.status-zone {
  margin-bottom: 16px;
}

.status-alert {
  font-size: 14px;
}

.footer {
  text-align: center;
  font-size: 14px;
  color: #475569;
}

.link {
  color: #0f172a;
  font-weight: 600;
  margin-left: 6px;
}
</style>
