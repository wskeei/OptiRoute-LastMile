import { describe, expect, it } from 'vitest'

import {
  buildAnalyticsSummary,
  getLatestCompletedPlan,
  getRecentCompletedPlans,
  sortPlansByNewest
} from '../lib/analytics'

describe('buildAnalyticsSummary', () => {
  it('keeps measured operations metrics separate from estimated optimization metrics', () => {
    const summary = buildAnalyticsSummary({
      couriers: [
        { id: 1, name: '张三', status: 'AVAILABLE' },
        { id: 2, name: '李四', status: 'BUSY' }
      ],
      packages: [
        { id: 1, status: 'PENDING', weight: 2.4 },
        { id: 2, status: 'ASSIGNED', weight: 1.1 },
        { id: 3, status: 'DELIVERED', weight: 3.5 }
      ],
      plans: [
        {
          id: 11,
          status: 'READY',
          routes: [
            {
              courier_id: 1,
              geo_json: {
                total_distance_km: 12.4,
                package_count: 2
              }
            },
            {
              courier_id: 2,
              geo_json: {
                total_distance_km: 8.6,
                package_count: 1
              }
            }
          ]
        }
      ]
    })

    expect(summary.factual.totalPackages).toBe(3)
    expect(summary.factual.pendingPackages).toBe(1)
    expect(summary.factual.totalPlans).toBe(1)
    expect(summary.factual.totalOptimizedDistance).toBe(21)
    expect(summary.factual.averagePackagesPerCourier).toBe(1.5)

    expect(summary.estimated.isEstimate).toBe(true)
    expect(summary.estimated.baselineDistance).toBe(26.25)
    expect(summary.estimated.savedDistance).toBe(5.25)
    expect(summary.estimated.savedRate).toBe(20)
    expect(summary.estimated.savedCost).toBe(32)
  })

  it('returns zeroed estimates when there is no completed dispatch result yet', () => {
    const summary = buildAnalyticsSummary({
      couriers: [],
      packages: [],
      plans: []
    })

    expect(summary.factual.totalPlans).toBe(0)
    expect(summary.factual.totalOptimizedDistance).toBe(0)
    expect(summary.estimated.baselineDistance).toBe(0)
    expect(summary.estimated.savedDistance).toBe(0)
    expect(summary.estimated.savedCost).toBe(0)
  })

  it('sorts plans explicitly by newest created_at before deriving latest and recent sets', () => {
    const plans = [
      {
        id: 7,
        created_at: '2026-04-01T10:00:00Z',
        status: 'COMPLETED',
        routes: [{ geo_json: { total_distance_km: 5, package_count: 1 }, courier_id: 2 }]
      },
      {
        id: 9,
        created_at: '2026-04-03T10:00:00Z',
        status: 'READY',
        routes: [{ geo_json: { total_distance_km: 4, package_count: 1 }, courier_id: 1 }]
      },
      {
        id: 8,
        created_at: '2026-04-02T10:00:00Z',
        status: 'READY',
        routes: [{ geo_json: { total_distance_km: 3, package_count: 1 }, courier_id: 3 }]
      }
    ]

    expect(sortPlansByNewest(plans).map((plan) => plan.id)).toEqual([9, 8, 7])
    expect(getLatestCompletedPlan(plans)?.id).toBe(9)
    expect(getRecentCompletedPlans(plans, 2).map((plan) => plan.id)).toEqual([8, 9])
  })
})
