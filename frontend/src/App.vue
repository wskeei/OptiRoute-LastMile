<template>
  <div v-if="isAuthPage" class="auth-layout">
    <router-view />
  </div>
  <div
    v-else
    class="app-shell"
    :class="{ 'shell-collapsed': collapsed && !isCompactNavigation }"
  >
    <aside class="sidebar" :class="{ collapsed }">
      <div class="sidebar-head">
        <router-link class="brand" to="/dispatch">
          <div class="brand-mark">OR</div>
          <div v-show="!collapsed" class="brand-copy">
            <strong>{{ PRODUCT_NAME }}</strong>
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

      <nav class="nav-list nav-primary" aria-label="主要导航">
        <router-link
          v-for="item in primaryNavItems"
          :key="item.path"
          :to="item.path"
          class="nav-link"
          :class="{ active: isActiveRoute(item.path) }"
        >
          <el-icon class="nav-icon">
            <component :is="item.icon" />
          </el-icon>
          <span v-show="!collapsed" class="nav-copy">
            <span class="nav-label">{{ item.label }}</span>
            <span v-if="showNavDescription(item.path, item.description)" class="nav-desc">
              {{ item.description }}
            </span>
          </span>
        </router-link>

        <button
          v-if="isCompactNavigation"
          class="nav-link nav-more"
          type="button"
          :aria-expanded="moreMenuOpen"
          aria-label="展开更多页面"
          @click="moreMenuOpen = !moreMenuOpen"
        >
          <el-icon class="nav-icon"><MoreFilled /></el-icon>
          <span class="nav-copy">
            <span class="nav-label">更多页面</span>
          </span>
        </button>
      </nav>

      <section v-if="!isCompactNavigation" class="nav-section">
        <p v-show="!collapsed" class="nav-section-label">辅助页面</p>
        <nav class="nav-list" aria-label="辅助导航">
          <router-link
            v-for="item in secondaryNavItems"
            :key="item.path"
            :to="item.path"
            class="nav-link"
            :class="{ active: isActiveRoute(item.path) }"
          >
            <el-icon class="nav-icon">
              <component :is="item.icon" />
            </el-icon>
            <span v-show="!collapsed" class="nav-copy">
              <span class="nav-label">{{ item.label }}</span>
              <span v-if="showNavDescription(item.path, item.description)" class="nav-desc">
                {{ item.description }}
              </span>
            </span>
          </router-link>
        </nav>
      </section>

      <section v-else-if="moreMenuOpen" class="mobile-more section-card">
        <p class="nav-section-label">辅助页面</p>
        <nav class="nav-list nav-secondary" aria-label="辅助导航">
          <router-link
            v-for="item in secondaryNavItems"
            :key="item.path"
            :to="item.path"
            class="nav-link"
            :class="{ active: isActiveRoute(item.path) }"
            @click="moreMenuOpen = false"
          >
            <el-icon class="nav-icon">
              <component :is="item.icon" />
            </el-icon>
            <span class="nav-copy">
              <span class="nav-label">{{ item.label }}</span>
              <span v-if="showNavDescription(item.path, item.description)" class="nav-desc">
                {{ item.description }}
              </span>
            </span>
          </router-link>
        </nav>
      </section>
    </aside>

    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, markRaw, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import {
  Box,
  Clock,
  Cpu,
  HomeFilled,
  Location,
  MoreFilled,
  Operation,
  Setting,
  TrendCharts,
  User
} from '@element-plus/icons-vue'

import {
  PRIMARY_NAV_ITEMS,
  PRODUCT_NAME,
  SECONDARY_NAV_ITEMS
} from './lib/ux'

const collapsed = ref(false)
const moreMenuOpen = ref(false)
const route = useRoute()
const isCompactNavigation = ref(false)

const iconMap = {
  Box: markRaw(Box),
  Clock: markRaw(Clock),
  Cpu: markRaw(Cpu),
  HomeFilled: markRaw(HomeFilled),
  Location: markRaw(Location),
  MoreFilled: markRaw(MoreFilled),
  Setting: markRaw(Setting),
  TrendCharts: markRaw(TrendCharts),
  User: markRaw(User)
}

const primaryNavItems = PRIMARY_NAV_ITEMS.map((item) => ({
  ...item,
  icon: iconMap[item.icon]
}))

const secondaryNavItems = SECONDARY_NAV_ITEMS.map((item) => ({
  ...item,
  icon: iconMap[item.icon]
}))

const isAuthPage = computed(
  () => route.path === '/login' || route.path === '/register' || route.meta.shell === false
)
const isActiveRoute = (path: string) => route.path === path
const showNavDescription = (path: string, description?: string) =>
  Boolean(description) && !collapsed.value && isActiveRoute(path)

const syncCompactNavigation = () => {
  if (typeof window === 'undefined') return
  isCompactNavigation.value = window.innerWidth <= 960
  if (!isCompactNavigation.value) {
    moreMenuOpen.value = false
  }
}

onMounted(() => {
  syncCompactNavigation()
  window.addEventListener('resize', syncCompactNavigation)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', syncCompactNavigation)
})
</script>

<style scoped>
.auth-layout {
  min-height: 100vh;
}

.app-shell {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 14.5rem minmax(0, 1fr);
  background:
    radial-gradient(circle at top left, rgba(62, 106, 138, 0.08), transparent 24rem),
    linear-gradient(180deg, #f5f7fa 0%, #edf2f7 100%);
}

.app-shell.shell-collapsed {
  grid-template-columns: 4.5rem minmax(0, 1fr);
}

.sidebar {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 0.875rem;
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

.app-shell.shell-collapsed .sidebar {
  padding-inline: 0.625rem;
}

.app-shell.shell-collapsed .sidebar-head {
  flex-direction: column;
  justify-content: flex-start;
}

.app-shell.shell-collapsed .brand {
  width: 100%;
  justify-content: center;
}

.app-shell.shell-collapsed .nav-link {
  padding-inline: 0.425rem;
}

.sidebar-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.brand {
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
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
  display: block;
  max-width: 100%;
  font-size: 0.88rem;
  line-height: 1.2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
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

.nav-list {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.nav-section {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.nav-section-label {
  margin: 0;
  color: #829ab1;
  font-size: 0.78rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.nav-link {
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.66rem 0.72rem;
  border-radius: 0.9rem;
  color: var(--text-strong);
  text-decoration: none;
  transition: background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease;
}

.nav-link:hover,
.nav-link:focus-visible {
  background: rgba(24, 74, 104, 0.08);
  outline: none;
}

.nav-link.active {
  background: var(--brand-strong);
  color: #f7fafc;
}

.nav-more {
  border: 1px dashed rgba(24, 74, 104, 0.14);
  background: rgba(255, 255, 255, 0.8);
  text-align: left;
  cursor: pointer;
}

.nav-icon {
  font-size: 1.1rem;
  flex-shrink: 0;
}

.nav-copy {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}

.nav-label {
  font-weight: 600;
  line-height: 1.25;
}

.nav-desc {
  color: var(--text-subtle);
  font-size: 0.78rem;
  line-height: 1.35;
}

.nav-link.active .nav-desc {
  color: rgba(247, 250, 252, 0.78);
}

.main-content {
  min-width: 0;
  padding: 1.5rem;
}

.mobile-more {
  display: none;
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

  .nav-list {
    flex-direction: row;
    flex-wrap: wrap;
  }

  .nav-link {
    min-width: calc(50% - 0.25rem);
  }

  .main-content {
    padding: 1rem;
  }

  .mobile-more {
    display: block;
  }

  .nav-secondary {
    flex-direction: column;
  }

  .nav-secondary .nav-link {
    min-width: 0;
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
    min-width: 100%;
    padding: 0.75rem 0.85rem;
  }
}
</style>
