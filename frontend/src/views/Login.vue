<template>
  <div class="login-container">
    <div class="background-decoration">
      <div class="circle circle-1"></div>
      <div class="circle circle-2"></div>
      <div class="circle circle-3"></div>
    </div>

    <div class="login-card glass-card">
      <div class="card-header">
        <div class="icon-wrapper">
          <el-icon :size="48"><Lock /></el-icon>
        </div>
        <h1>欢迎回来</h1>
        <p class="subtitle">登录 AI 智能配送调度系统</p>
      </div>

      <el-form :model="form" class="login-form">
        <el-form-item>
          <el-input
            v-model="form.username"
            placeholder="用户名"
            size="large"
            :prefix-icon="User"
            clearable
          />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
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
          class="login-button"
        >
          <span v-if="!loading">立即登录</span>
          <span v-else>登录中...</span>
        </el-button>
      </el-form>

      <div class="footer">
        <span>还没有账号？</span>
        <router-link to="/register" class="link">立即注册</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  username: '',
  password: ''
})

const loading = ref(false)

const handleLogin = async () => {
  if (!form.value.username || !form.value.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }

  loading.value = true
  try {
    await authStore.login(form.value.username, form.value.password)
    ElMessage.success('登录成功！欢迎回来')
    router.push('/dashboard')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '登录失败，请检查用户名和密码')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow: hidden;
}

.background-decoration {
  position: absolute;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  animation: float 20s infinite ease-in-out;
}

.circle-1 {
  width: 300px;
  height: 300px;
  top: -100px;
  left: -100px;
  animation-delay: 0s;
}

.circle-2 {
  width: 200px;
  height: 200px;
  bottom: -50px;
  right: -50px;
  animation-delay: 5s;
}

.circle-3 {
  width: 150px;
  height: 150px;
  top: 50%;
  right: 10%;
  animation-delay: 10s;
}

@keyframes float {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-30px) scale(1.1); }
}

.login-card {
  width: 440px;
  padding: 48px;
  position: relative;
  z-index: 1;
  animation: slideUp 0.6s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.glass-card {
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(30px);
  border-radius: 24px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.card-header {
  text-align: center;
  margin-bottom: 36px;
}

.icon-wrapper {
  width: 80px;
  height: 80px;
  margin: 0 auto 20px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
}

h1 {
  margin: 0 0 12px 0;
  font-size: 32px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: -0.5px;
}

.subtitle {
  margin: 0;
  color: #718096;
  font-size: 15px;
  font-weight: 500;
}

.login-form {
  margin-bottom: 28px;
}

.el-form-item {
  margin-bottom: 20px;
}

:deep(.el-input__wrapper) {
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.25);
}

.login-button {
  width: 100%;
  height: 48px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border: none;
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
  transition: all 0.3s;
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 28px rgba(102, 126, 234, 0.4);
}

.login-button:active {
  transform: translateY(0);
}

.footer {
  text-align: center;
  font-size: 15px;
  color: #718096;
  padding-top: 24px;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
}

.link {
  color: #667eea;
  text-decoration: none;
  margin-left: 8px;
  font-weight: 600;
  transition: all 0.3s;
}

.link:hover {
  color: #764ba2;
  text-decoration: underline;
}
</style>
