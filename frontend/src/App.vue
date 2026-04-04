<template>
  <div v-if="isAuthPage" class="auth-layout">
    <router-view />
  </div>
  <div v-else class="app-shell">
    <aside class="sidebar" :class="{ collapsed }">
      <div class="sidebar-head">
        <router-link class="brand" to="/dispatch">
          <div class="brand-mark">OR</div>
          <div v-show="!collapsed" class="brand-copy">
            <strong>{{ PRODUCT_NAME }}</strong>
            <span>{{ PRODUCT_ENVIRONMENT_LABEL }}</span>
          </div>
        </router-link>

        <button
          class="sidebar-toggle"
          type="button"
          :aria-expanded="!collapsed"
          :aria-label="collapsed ? '展开导航' : '收起导航'"
          @click="collapsed = !collapsed"
        >
          <el-icon><Operation /></el-icon>
        </button>
      </div>

      <p v-show="!collapsed" class="sidebar-summary">
        先重置演示数据，再启动调度，然后查看路线结果。
      </p>

      <nav class="nav-list" aria-label="主要导航">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="nav-link"
          :class="{ active: $route.path === item.path }"
        >
          <el-icon class="nav-icon">
            <component :is="item.icon" />
          </el-icon>
          <span v-show="!collapsed" class="nav-copy">
            <span class="nav-label">{{ item.label }}</span>
            <span class="nav-desc">{{ item.description }}</span>
          </span>
        </router-link>
      </nav>
    </aside>

    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, markRaw, ref } from 'vue'
import { useRoute } from 'vue-router'
import {
  Box,
  Clock,
  Cpu,
  HomeFilled,
  Location,
  Operation,
  Setting,
  TrendCharts,
  User
} from '@element-plus/icons-vue'

import { NAV_ITEMS, PRODUCT_ENVIRONMENT_LABEL, PRODUCT_NAME } from './lib/ux'

const collapsed = ref(false)
const route = useRoute()

const iconMap = {
  Box: markRaw(Box),
  Clock: markRaw(Clock),
  Cpu: markRaw(Cpu),
  HomeFilled: markRaw(HomeFilled),
  Location: markRaw(Location),
  Setting: markRaw(Setting),
  TrendCharts: markRaw(TrendCharts),
  User: markRaw(User)
}

const navItems = NAV_ITEMS.map((item) => ({
  ...item,
  icon: iconMap[item.icon]
}))

const isAuthPage = computed(() => route.path === '/login' || route.path === '/register')
</script>

<style scoped>
.auth-layout {
  min-height: 100vh;
}

.app-shell {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 18rem minmax(0, 1fr);
  background:
    radial-gradient(circle at top left, rgba(62, 106, 138, 0.08), transparent 24rem),
    linear-gradient(180deg, #f5f7fa 0%, #edf2f7 100%);
}

.sidebar {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1.25rem;
  border-right: 1px solid rgba(85, 103, 122, 0.12);
  background: rgba(247, 250, 252, 0.94);
  backdrop-filter: blur(12px);
}

.sidebar.collapsed {
  align-items: center;
}

.sidebar.collapsed .nav-link {
  justify-content: center;
}

.sidebar-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.brand {
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: #1f2933;
  text-decoration: none;
}

.brand-mark {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.85rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #184a68;
  color: #f7fafc;
  font-size: 0.875rem;
  font-weight: 700;
  letter-spacing: 0.08em;
}

.brand-copy {
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.brand-copy strong {
  font-size: 0.95rem;
}

.brand-copy span {
  color: #52606d;
  font-size: 0.82rem;
}

.sidebar-toggle {
  width: 2.5rem;
  height: 2.5rem;
  border: 1px solid rgba(85, 103, 122, 0.18);
  border-radius: 0.85rem;
  background: #ffffff;
  color: #243b53;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.sidebar-summary {
  margin: 0;
  padding: 0.875rem 1rem;
  border-radius: 1rem;
  background: rgba(224, 232, 240, 0.55);
  color: #486581;
  font-size: 0.9rem;
  line-height: 1.5;
}

.nav-list {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.nav-link {
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 0.875rem;
  padding: 0.85rem 0.95rem;
  border-radius: 1rem;
  color: #243b53;
  text-decoration: none;
  transition: background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease;
}

.nav-link:hover,
.nav-link:focus-visible {
  background: rgba(24, 74, 104, 0.08);
  outline: none;
}

.nav-link.active {
  background: #184a68;
  color: #f7fafc;
}

.nav-icon {
  font-size: 1.1rem;
  flex-shrink: 0;
}

.nav-copy {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.nav-label {
  font-weight: 600;
}

.nav-desc {
  color: inherit;
  opacity: 0.72;
  font-size: 0.8rem;
  line-height: 1.35;
}

.main-content {
  min-width: 0;
  padding: 1.5rem;
}

@media (max-width: 960px) {
  .app-shell {
    grid-template-columns: 1fr;
  }

  .sidebar {
    padding: 1rem;
    border-right: none;
    border-bottom: 1px solid rgba(85, 103, 122, 0.12);
  }

  .sidebar-toggle {
    display: none;
  }

  .sidebar-summary {
    display: none;
  }

  .nav-list {
    flex-direction: row;
    overflow-x: auto;
    padding-bottom: 0.25rem;
  }

  .nav-link {
    min-width: 11rem;
  }

  .main-content {
    padding: 1rem;
  }
}

@media (max-width: 640px) {
  .sidebar {
    gap: 0.75rem;
  }

  .brand-copy strong {
    font-size: 0.88rem;
  }

  .brand-copy span {
    font-size: 0.75rem;
  }

  .nav-link {
    min-width: 10rem;
    padding: 0.75rem 0.85rem;
  }
}
</style>
