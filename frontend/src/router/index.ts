import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/dashboard'
    },
    {
      path: '/dashboard',
      name: 'Dashboard',
      component: () => import('../views/Dashboard.vue')
    },
    {
      path: '/dispatch',
      name: 'SmartDispatch',
      component: () => import('../views/SmartDispatch.vue')
    },
    {
      path: '/packages',
      name: 'PackageFlow',
      component: () => import('../views/PackageFlow.vue')
    },
    {
      path: '/couriers',
      name: 'CourierWork',
      component: () => import('../views/CourierWork.vue')
    },
    {
      path: '/monitor',
      name: 'RealtimeMap',
      component: () => import('../views/RealtimeMap.vue')
    },
    {
      path: '/analytics',
      name: 'Analytics',
      component: () => import('../views/Analytics.vue')
    },
    {
      path: '/history',
      name: 'RouteHistory',
      component: () => import('../views/RouteHistory.vue')
    },
    {
      path: '/settings',
      name: 'Settings',
      component: () => import('../views/Settings.vue')
    }
  ]
})

export default router
