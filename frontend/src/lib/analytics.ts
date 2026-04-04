interface AnalyticsInput {
  plans: any[]
  packages: any[]
  couriers: any[]
}

const COMPLETED_PLAN_STATUSES = new Set(['READY', 'COMPLETED'])

const round = (value: number, digits = 2) => Number(value.toFixed(digits))

export const getCompletedPlans = (plans: any[]) =>
  plans.filter((plan: any) => COMPLETED_PLAN_STATUSES.has(plan.status) && plan.routes?.length > 0)

export const buildAnalyticsSummary = ({ plans, packages, couriers }: AnalyticsInput) => {
  const completedPlans = getCompletedPlans(plans)
  const latestPlan = completedPlans[0]

  const totalOptimizedDistance = round(
    completedPlans.reduce(
      (planSum: number, plan: any) =>
        planSum +
        (plan.routes?.reduce(
          (routeSum: number, route: any) => routeSum + (route.geo_json?.total_distance_km || 0),
          0
        ) || 0),
      0
    ),
    2
  )

  const totalWeight = round(
    packages.reduce((sum: number, item: any) => sum + (item.weight || 0), 0),
    1
  )

  const latestPlanPackageCount = latestPlan?.routes?.reduce(
    (sum: number, route: any) => sum + (route.geo_json?.package_count || 0),
    0
  ) || 0

  const latestPlanCourierCount = new Set(
    latestPlan?.routes?.map((route: any) => route.courier_id).filter(Boolean) || []
  ).size

  const averagePackagesPerCourier =
    latestPlanCourierCount > 0 ? round(latestPlanPackageCount / latestPlanCourierCount, 1) : 0
  const averageDistancePerPackage =
    latestPlanPackageCount > 0 ? round(totalOptimizedDistance / latestPlanPackageCount, 2) : 0

  const baselineDistance = totalOptimizedDistance > 0 ? round(totalOptimizedDistance * 1.25, 2) : 0
  const savedDistance = totalOptimizedDistance > 0 ? round(baselineDistance - totalOptimizedDistance, 2) : 0
  const savedRate = totalOptimizedDistance > 0 ? 20 : 0
  const savedCost = Math.round(savedDistance * 6)

  return {
    factual: {
      totalPackages: packages.length,
      pendingPackages: packages.filter((item: any) => item.status === 'PENDING').length,
      totalCouriers: couriers.length,
      totalPlans: completedPlans.length,
      totalWeight,
      totalOptimizedDistance,
      averagePackagesPerCourier,
      averageDistancePerPackage
    },
    estimated: {
      isEstimate: true,
      baselineDistance,
      savedDistance,
      savedRate,
      savedCost
    }
  }
}
