export interface NavItem {
  path: string
  label: string
  description: string
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
export const PRODUCT_SUMMARY = '用于展示调度、路线生成和结果复盘的前端演示环境。'

export const NAV_ITEMS: NavItem[] = [
  {
    path: '/dispatch',
    label: '调度中心',
    description: '重置样本数据并发起一次调度',
    icon: 'Cpu'
  },
  {
    path: '/monitor',
    label: '路线监控',
    description: '查看最近一次调度的路线与配送进度',
    icon: 'Location'
  },
  {
    path: '/history',
    label: '调度历史',
    description: '复盘历史计划与路线详情',
    icon: 'Clock'
  },
  {
    path: '/dashboard',
    label: '任务概览',
    description: '查看当前演示环境与下一步建议',
    icon: 'HomeFilled'
  },
  {
    path: '/packages',
    label: '包裹数据',
    description: '查看或补充演示包裹样本',
    icon: 'Box'
  },
  {
    path: '/couriers',
    label: '快递员数据',
    description: '查看可参与调度的快递员样本',
    icon: 'User'
  },
  {
    path: '/analytics',
    label: '运营分析',
    description: '区分实际统计与演示估算',
    icon: 'TrendCharts'
  },
  {
    path: '/settings',
    label: '系统说明',
    description: '查看演示环境规则与数据维护入口',
    icon: 'Setting'
  }
]

export const ONBOARDING_STEPS: OnboardingStep[] = [
  {
    title: '1. 重置演示数据',
    description: '生成一批待调度包裹和可用快递员，确保本轮演示有样本可跑。',
    actionLabel: '前往调度中心',
    path: '/dispatch'
  },
  {
    title: '2. 启动一次调度',
    description: '创建计划并等待后端输出实际路线，地图和历史页会基于该结果更新。',
    actionLabel: '开始调度',
    path: '/dispatch'
  },
  {
    title: '3. 查看路线结果',
    description: '在路线监控和历史页查看最新路线、配送进度和计划详情。',
    actionLabel: '查看路线监控',
    path: '/monitor'
  }
]

export const DISPATCH_TRUTH_NOTES = [
  '聚类数会根据当前可用快递员数量自动确定，前端不会直接控制 K 值。',
  '遗传算法迭代次数和种群规模使用后端固定配置，当前界面不提供真实调参入口。',
  '地图路线、路线总距离和配送状态来自后端实际返回；演示数据由“重置演示数据”接口随机生成。'
]

export const SETTINGS_TRUTH_NOTES = [
  '当前系统展示的是演示流程，不是生产调度后台。',
  '如果需要展示真实可调参数，应先让后端显式接收并执行这些参数。',
  '分析页中的“节省率/成本”属于演示估算，页面会明确标注来源。'
]
