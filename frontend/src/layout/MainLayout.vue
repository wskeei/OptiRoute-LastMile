<template>
  <el-container class="layout-container">
    <!-- 悬浮侧边栏 -->
    <aside class="glass-sidebar">
      <div class="logo">
        <div class="logo-icon-bg">
          <el-icon class="logo-icon"><Van /></el-icon>
        </div>
        <span class="logo-text">SmartDispatch</span>
      </div>
      
      <div class="menu-container">
        <el-menu
          :default-active="activeMenu"
          class="el-menu-vertical glass-menu"
          router
          :collapse="false"
        >
          <div class="menu-group-title">核心功能</div>
          <el-menu-item index="/dashboard">
            <el-icon><Odometer /></el-icon>
            <span>智能工作台</span>
          </el-menu-item>
          <el-menu-item index="/dispatch">
            <el-icon><Cpu /></el-icon>
            <span>AI调度中心</span>
          </el-menu-item>
          
          <div class="menu-group-title">运营管理</div>
          <el-menu-item index="/packages">
            <el-icon><Box /></el-icon>
            <span>包裹流转</span>
          </el-menu-item>
          <el-menu-item index="/couriers">
            <el-icon><User /></el-icon>
            <span>运力监控</span>
          </el-menu-item>
          <el-menu-item index="/monitor">
            <el-icon><MapLocation /></el-icon>
            <span>实时地图</span>
          </el-menu-item>
          
          <div class="menu-group-title">数据与设置</div>
          <el-menu-item index="/analytics">
            <el-icon><DataAnalysis /></el-icon>
            <span>数据分析</span>
          </el-menu-item>
          <el-menu-item index="/history">
            <el-icon><History /></el-icon>
            <span>历史回溯</span>
          </el-menu-item>
          <el-menu-item index="/settings">
            <el-icon><Setting /></el-icon>
            <span>系统设置</span>
          </el-menu-item>
        </el-menu>
      </div>

      <div class="user-profile">
        <el-avatar :size="40" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" />
        <div class="user-info">
          <div class="user-name">Admin User</div>
          <div class="user-role">总调度员</div>
        </div>
      </div>
    </aside>
    
    <el-container class="main-wrapper">
      <!-- 隐形 Header，只保留面包屑和功能区 -->
      <header class="glass-header">
        <div class="header-left">
          <h2 class="page-title">{{ currentRouteName }}</h2>
          <span class="date-badge">{{ currentDate }}</span>
        </div>
        <div class="header-right">
          <el-button circle :icon="Search" />
          <el-button circle :icon="Bell" />
          <el-button type="primary" round>
            <el-icon class="el-icon--left"><Plus /></el-icon> 新建任务
          </el-button>
        </div>
      </header>
      
      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade-slide" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { Search, Bell, Plus } from '@element-plus/icons-vue'

const route = useRoute()
const activeMenu = computed(() => route.path)
const currentRouteName = computed(() => route.meta.title || 'Dashboard')
const currentDate = new Date().toLocaleDateString('zh-CN', { month: 'short', day: 'numeric', weekday: 'short' })
</script>

<style scoped>
.layout-container {
  display: flex;
  height: 100vh;
  padding: 20px;
  box-sizing: border-box;
  overflow: hidden;
}

/* 玻璃侧边栏 */
.glass-sidebar {
  width: var(--sidebar-width);
  height: calc(100vh - 40px);
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  border-radius: var(--border-radius-lg);
  display: flex;
  flex-direction: column;
  padding: 20px;
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
  border: 1px solid rgba(255, 255, 255, 0.5);
  z-index: 100;
  margin-right: 20px;
}

.logo {
  display: flex;
  align-items: center;
  padding: 10px 10px 30px;
}

.logo-icon-bg {
  width: 40px;
  height: 40px;
  background: var(--primary-gradient);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-right: 12px;
  box-shadow: 0 4px 10px rgba(102, 126, 234, 0.4);
}

.logo-text {
  font-size: 18px;
  font-weight: 800;
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.menu-container {
  flex: 1;
  overflow-y: auto;
}

/* 菜单样式重写 */
.glass-menu {
  border-right: none;
  background: transparent;
}

.menu-group-title {
  font-size: 12px;
  color: #a0aec0;
  margin: 20px 0 10px 20px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.el-menu-item {
  height: 50px;
  line-height: 50px;
  border-radius: 12px;
  margin-bottom: 5px;
  color: var(--text-secondary);
}

.el-menu-item:hover {
  background: rgba(255, 255, 255, 0.6);
  color: var(--primary-color);
}

.el-menu-item.is-active {
  background: var(--primary-gradient);
  color: white;
  box-shadow: 0 4px 12px rgba(118, 75, 162, 0.3);
  font-weight: 600;
}

/* 用户卡片 */
.user-profile {
  display: flex;
  align-items: center;
  padding: 15px;
  background: white;
  border-radius: 16px;
  margin-top: 20px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.03);
}

.user-info {
  margin-left: 12px;
}

.user-name {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-main);
}

.user-role {
  font-size: 12px;
  color: #a0aec0;
}

/* 主内容区 */
.main-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 40px);
}

.glass-header {
  height: 70px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 10px;
  margin-bottom: 10px;
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 800;
  color: #2d3748;
  display: inline-block;
  margin-right: 15px;
}

.date-badge {
  background: rgba(255, 255, 255, 0.6);
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 13px;
  color: #718096;
  font-weight: 600;
}

.main-content {
  flex: 1;
  padding: 0 10px;
  overflow-y: auto;
  overflow-x: hidden;
}

/* 路由动画 */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.4s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}
</style>