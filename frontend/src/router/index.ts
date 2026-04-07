import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { AUTH_REDIRECT_ROUTE, DEFAULT_ROUTE } from '../lib/ux'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: DEFAULT_ROUTE
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('../views/Login.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('../views/Register.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/dashboard',
      name: 'Dashboard',
      component: () => import('../views/Dashboard.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/dispatch',
      name: 'SmartDispatch',
      component: () => import('../views/SmartDispatch.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/packages',
      name: 'PackageFlow',
      component: () => import('../views/PackageFlow.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/couriers',
      name: 'CourierWork',
      component: () => import('../views/CourierWork.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/monitor',
      name: 'RealtimeMap',
      component: () => import('../views/RealtimeMap.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/analytics',
      name: 'Analytics',
      component: () => import('../views/Analytics.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/history',
      name: 'RouteHistory',
      component: () => import('../views/RouteHistory.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/settings',
      name: 'Settings',
      component: () => import('../views/Settings.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/thesis/figure-4-5',
      name: 'ThesisFigure45',
      component: () => import('../views/ThesisFigure45.vue'),
      meta: { requiresAuth: false, shell: false }
    }
  ]
})

// 路由守卫
router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()

  // 如果路由需要认证且用户未登录，跳转到登录页
  if (to.meta.requiresAuth !== false && !authStore.isAuthenticated) {
    next('/login')
  }
  // 如果已登录用户访问登录页，跳转到首页
  else if (to.path === '/login' && authStore.isAuthenticated) {
    next(AUTH_REDIRECT_ROUTE)
  }
  else {
    next()
  }
})

export default router
