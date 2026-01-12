import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import MainLayout from '../layout/MainLayout.vue'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    component: MainLayout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue'),
        meta: { title: '智能工作台' }
      },
      {
        path: 'dispatch',
        name: 'Dispatch',
        component: () => import('../views/SmartDispatch.vue'),
        meta: { title: 'AI调度中心' }
      },
      {
        path: 'packages',
        name: 'Packages',
        component: () => import('../views/PackageFlow.vue'),
        meta: { title: '包裹流转中心' }
      },
      {
        path: 'couriers',
        name: 'Couriers',
        component: () => import('../views/CourierWork.vue'),
        meta: { title: '快递员工作台' }
      },
      {
        path: 'monitor',
        name: 'Monitor',
        component: () => import('../views/RealtimeMap.vue'),
        meta: { title: '实时监控地图' }
      },
      {
        path: 'analytics',
        name: 'Analytics',
        component: () => import('../views/DeliveryAnalytics.vue'),
        meta: { title: '配送分析中心' }
      },
      {
        path: 'history',
        name: 'History',
        component: () => import('../views/RouteHistory.vue'),
        meta: { title: '路线优化历史' }
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('../views/SystemSettings.vue'),
        meta: { title: '系统设置' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router