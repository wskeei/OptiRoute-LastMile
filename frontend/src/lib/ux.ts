export interface NavItem {
  path: string
  label: string
  description?: string
  icon: 'Cpu' | 'Location' | 'Clock' | 'HomeFilled' | 'Box' | 'User' | 'TrendCharts' | 'Setting'
}

export interface OnboardingStep {
  title: string
  description: string
  actionLabel: string
  path: string
}

export const PRIMARY_ROUTE = '/dispatch'
export const DEFAULT_ROUTE = PRIMARY_ROUTE
export const AUTH_REDIRECT_ROUTE = PRIMARY_ROUTE

export const PRODUCT_NAME = '末端配送调度演示系统'
export const PRODUCT_ENVIRONMENT_LABEL = '演示环境'
export const PRODUCT_SUMMARY = '调度、监控与复盘演示。'
export const PRODUCT_ENVIRONMENT_NOTE = '演示数据与估算结果会单独标注。'

export const NAV_ITEMS: NavItem[] = [
  {
    path: '/dispatch',
    label: '调度中心',
    description: '发起调度',
    icon: 'Cpu'
  },
  {
    path: '/monitor',
    label: '路线监控',
    description: '查看结果',
    icon: 'Location'
  },
  {
    path: '/history',
    label: '调度历史',
    description: '复盘记录',
    icon: 'Clock'
  },
  {
    path: '/dashboard',
    label: '任务概览',
    description: '查看概览',
    icon: 'HomeFilled'
  },
  {
    path: '/packages',
    label: '包裹数据',
    description: '查看样本',
    icon: 'Box'
  },
  {
    path: '/couriers',
    label: '快递员数据',
    description: '查看人员',
    icon: 'User'
  },
  {
    path: '/analytics',
    label: '运营分析',
    description: '查看估算',
    icon: 'TrendCharts'
  },
  {
    path: '/settings',
    label: '系统说明',
    description: '维护说明',
    icon: 'Setting'
  }
]

export const PRIMARY_NAV_ITEMS = NAV_ITEMS.filter((item) =>
  ['/dispatch', '/monitor', '/history', '/dashboard'].includes(item.path)
)

export const SECONDARY_NAV_ITEMS = NAV_ITEMS.filter((item) =>
  ['/packages', '/couriers', '/analytics', '/settings'].includes(item.path)
)

export const ONBOARDING_STEPS: OnboardingStep[] = [
  {
    title: '1. 重置数据',
    description: '生成待调度样本。',
    actionLabel: '前往调度中心',
    path: '/dispatch'
  },
  {
    title: '2. 启动一次调度',
    description: '发起调度并等待结果。',
    actionLabel: '开始调度',
    path: '/dispatch'
  },
  {
    title: '3. 查看路线结果',
    description: '查看路线与进度。',
    actionLabel: '查看路线监控',
    path: '/monitor'
  }
]

export const DISPATCH_TRUTH_NOTES = [
  '聚类数会根据当前可用快递员数量自动确定，前端不会直接控制 K 值。',
  '遗传算法迭代次数和种群规模使用后端固定配置，当前界面不提供真实调参入口。',
  '地图路线、路线总距离和配送状态来自后端实际返回；演示数据由“重置数据”操作随机生成。'
]
