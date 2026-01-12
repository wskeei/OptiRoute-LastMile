<template>
  <div v-if="isAuthPage" class="auth-layout">
    <router-view />
  </div>
  <el-container v-else class="app-container">
    <el-aside :width="collapsed ? '64px' : '240px'" class="sidebar">
      <div class="logo" @click="collapsed = !collapsed">
        <el-icon><Operation /></el-icon>
        <span v-show="!collapsed">智能配送系统</span>
      </div>
      <el-menu :default-active="$route.path" router :collapse="collapsed">
        <el-menu-item index="/dashboard">
          <el-icon><HomeFilled /></el-icon>
          <span>智能工作台</span>
        </el-menu-item>
        <el-menu-item index="/dispatch">
          <el-icon><Cpu /></el-icon>
          <span>AI调度中心</span>
        </el-menu-item>
        <el-menu-item index="/packages">
          <el-icon><Box /></el-icon>
          <span>包裹流转中心</span>
        </el-menu-item>
        <el-menu-item index="/couriers">
          <el-icon><User /></el-icon>
          <span>快递员工作台</span>
        </el-menu-item>
        <el-menu-item index="/monitor">
          <el-icon><Location /></el-icon>
          <span>实时监控地图</span>
        </el-menu-item>
        <el-menu-item index="/analytics">
          <el-icon><TrendCharts /></el-icon>
          <span>配送分析中心</span>
        </el-menu-item>
        <el-menu-item index="/history">
          <el-icon><Clock /></el-icon>
          <span>路线优化历史</span>
        </el-menu-item>
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <span>系统设置</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-main class="main-content">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'

const collapsed = ref(false)
const route = useRoute()

const isAuthPage = computed(() => {
  return route.path === '/login' || route.path === '/register'
})
</script>

<style>
html, body, #app {
  margin: 0;
  padding: 0;
  height: 100%;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
}

.app-container {
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.sidebar {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
  transition: width 0.3s;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  font-size: 18px;
  font-weight: bold;
  color: #667eea;
  cursor: pointer;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.main-content {
  padding: 20px;
  overflow-y: auto;
}

.el-menu {
  border: none;
  background: transparent;
}

.el-menu-item {
  margin: 4px 8px;
  border-radius: 8px;
}

.el-menu-item.is-active {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
}
</style>