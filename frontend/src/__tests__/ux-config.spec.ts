import { describe, expect, it } from 'vitest'

import {
  AUTH_REDIRECT_ROUTE,
  DEFAULT_ROUTE,
  DISPATCH_TRUTH_NOTES,
  PRODUCT_ENVIRONMENT_LABEL,
  PRODUCT_NAME,
  NAV_ITEMS,
  PRIMARY_NAV_ITEMS,
  SECONDARY_NAV_ITEMS,
  ONBOARDING_STEPS,
  PRIMARY_ROUTE
} from '../lib/ux'

describe('ux config', () => {
  it('makes dispatch the primary route for new and returning users', () => {
    expect(PRIMARY_ROUTE).toBe('/dispatch')
    expect(DEFAULT_ROUTE).toBe(PRIMARY_ROUTE)
    expect(AUTH_REDIRECT_ROUTE).toBe(PRIMARY_ROUTE)
  })

  it('prioritizes operational pages before analysis pages in navigation', () => {
    expect(NAV_ITEMS[0]?.path).toBe('/dispatch')
    expect(NAV_ITEMS.findIndex((item) => item.path === '/monitor')).toBeLessThan(
      NAV_ITEMS.findIndex((item) => item.path === '/analytics')
    )
    expect(NAV_ITEMS.findIndex((item) => item.path === '/history')).toBeLessThan(
      NAV_ITEMS.findIndex((item) => item.path === '/analytics')
    )
  })

  it('keeps mobile primary navigation focused on core tasks', () => {
    expect(PRIMARY_NAV_ITEMS.map((item) => item.path)).toEqual([
      '/dispatch',
      '/monitor',
      '/history',
      '/dashboard'
    ])
    expect(SECONDARY_NAV_ITEMS.map((item) => item.path)).toEqual([
      '/packages',
      '/couriers',
      '/analytics',
      '/settings'
    ])
  })

  it('teaches the demo workflow in the order users need to follow', () => {
    expect(ONBOARDING_STEPS.map((step) => step.path)).toEqual([
      '/dispatch',
      '/dispatch',
      '/monitor'
    ])
    expect(ONBOARDING_STEPS.map((step) => step.description)).toEqual([
      '生成待调度样本。',
      '发起调度并等待结果。',
      '查看路线与进度。'
    ])
  })

  it('contains explicit notes about which dispatch inputs are not backend controls', () => {
    expect(DISPATCH_TRUTH_NOTES.join(' ')).toContain('聚类数会根据当前可用快递员数量自动确定')
    expect(DISPATCH_TRUTH_NOTES.join(' ')).toContain('遗传算法迭代次数和种群规模使用后端固定配置')
  })

  it('keeps shared navigation copy short and scannable', () => {
    expect(PRODUCT_NAME).toBe('配送调度系统')
    expect(PRODUCT_ENVIRONMENT_LABEL).toBe('演示环境')
    expect(PRIMARY_NAV_ITEMS.map((item) => item.description)).toEqual([
      '发起调度',
      '查看结果',
      '复盘记录',
      '查看概览'
    ])
    expect(NAV_ITEMS.find((item) => item.path === '/settings')?.label).toBe('系统设置')
  })
})
