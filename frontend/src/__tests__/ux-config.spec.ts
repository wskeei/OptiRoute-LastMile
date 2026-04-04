import { describe, expect, it } from 'vitest'

import {
  AUTH_REDIRECT_ROUTE,
  DEFAULT_ROUTE,
  DISPATCH_TRUTH_NOTES,
  NAV_ITEMS,
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

  it('teaches the demo workflow in the order users need to follow', () => {
    expect(ONBOARDING_STEPS.map((step) => step.path)).toEqual([
      '/dispatch',
      '/dispatch',
      '/monitor'
    ])
  })

  it('contains explicit notes about which dispatch inputs are not backend controls', () => {
    expect(DISPATCH_TRUTH_NOTES.join(' ')).toContain('聚类数会根据当前可用快递员数量自动确定')
    expect(DISPATCH_TRUTH_NOTES.join(' ')).toContain('遗传算法迭代次数和种群规模使用后端固定配置')
  })
})
