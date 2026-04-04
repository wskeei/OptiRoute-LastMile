# Chart Render Timing Fix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the blank chart regressions on dashboard, analytics, and route history by ensuring ECharts initializes only after conditionally rendered chart containers are mounted.

**Architecture:** This is a lifecycle timing bug, not a data bug. The fix should preserve the current data sources and chart options, and only change when chart initialization runs. Use small, page-local timing fixes with `nextTick()` and explicit guards instead of introducing broad architectural changes.

**Tech Stack:** Vue 3, TypeScript, ECharts, Vue Test Utils, Vitest, Vite

---

## Debug Baseline

- Root cause already identified:
  - chart sections are rendered by `v-if` / `v-else-if`
  - reactive state is updated first
  - `echarts.init(...)` is called in the same tick
  - the chart DOM node is not mounted yet, so the `ref` is still empty
  - initialization is skipped and never retried
- This affects:
  - `frontend/src/views/Dashboard.vue`
  - `frontend/src/views/Analytics.vue`
  - `frontend/src/views/RouteHistory.vue`

## File Map

- Modify: `frontend/src/views/Dashboard.vue`
  - wait for DOM update before initializing `chartRef` / `courierChartRef`
- Modify: `frontend/src/views/Analytics.vue`
  - wait for DOM update before initializing `trendChartRef`, `courierChartRef`, `packageStatusChartRef`, and `courierStatusChartRef`
- Modify: `frontend/src/views/RouteHistory.vue`
  - wait for DOM update before initializing `trendChartRef`
- Modify: `frontend/src/__tests__/PageFeedback.spec.ts`
  - add regression tests asserting dashboard and analytics actually initialize ECharts in success states
- Modify: `frontend/src/__tests__/RouteHistory.spec.ts`
  - add regression test asserting history trend chart initializes when completed plans exist

## Implementation Rules

- Do not change chart data semantics or chart option structure unless required for the timing fix.
- Do not “fix” this by removing conditional rendering.
- Do not add arbitrary timeouts where `nextTick()` is sufficient.
- Do not mix unrelated cleanup into this patch.
- Prefer:
  - `await nextTick()` after state updates that unlock chart sections
  - clear `if (ref.value)` guards
  - focused regression tests around `echarts.init`

### Task 1: Add Failing Regression Tests For Chart Initialization

**Files:**
- Modify: `frontend/src/__tests__/PageFeedback.spec.ts`
- Modify: `frontend/src/__tests__/RouteHistory.spec.ts`

- [ ] **Step 1: Write a failing dashboard chart regression test**

Add a test in `frontend/src/__tests__/PageFeedback.spec.ts` that:
- mocks successful dashboard API responses with at least one completed plan
- mounts `Dashboard.vue`
- waits for `flushPromises()`
- asserts `echarts.init` was called for the dashboard chart containers

Suggested assertion shape:

```ts
import * as echarts from 'echarts'

expect(vi.mocked(echarts.init)).toHaveBeenCalled()
```

If needed, strengthen it by asserting call count `>= 1` or `>= 2`.

- [ ] **Step 2: Run the dashboard regression test and confirm it fails**

Run:
```bash
cd frontend && npm run test:unit -- PageFeedback
```

Expected:
- the new dashboard success-state chart-init assertion fails
- failure indicates `echarts.init` was not called in the success path

- [ ] **Step 3: Write a failing analytics chart regression test**

In `frontend/src/__tests__/PageFeedback.spec.ts`, add a second success-state test that:
- mocks plans, packages, and couriers with at least one completed plan
- mounts `Analytics.vue`
- waits for `flushPromises()`
- asserts `echarts.init` was called for analytics chart containers

Expected failure before the fix:
- textual content appears
- `echarts.init` assertion fails because the chart refs were still empty when initialization ran

- [ ] **Step 4: Write a failing route history chart regression test**

In `frontend/src/__tests__/RouteHistory.spec.ts`, add a test that:
- mocks one completed history plan
- mounts `RouteHistory.vue`
- waits for `flushPromises()`
- asserts `echarts.init` was called for the history trend chart

- [ ] **Step 5: Run the route history regression test and confirm it fails**

Run:
```bash
cd frontend && npm run test:unit -- RouteHistory
```

Expected:
- the new trend-chart initialization assertion fails before the implementation change

- [ ] **Step 6: Commit**

```bash
git add frontend/src/__tests__/PageFeedback.spec.ts frontend/src/__tests__/RouteHistory.spec.ts
git commit -m "test: add chart initialization regression coverage"
```

### Task 2: Fix Dashboard Chart Initialization Timing

**Files:**
- Modify: `frontend/src/views/Dashboard.vue`
- Test: `frontend/src/__tests__/PageFeedback.spec.ts`

- [ ] **Step 1: Import `nextTick` in `frontend/src/views/Dashboard.vue`**

Change:

```ts
import { onMounted, ref } from 'vue'
```

To:

```ts
import { nextTick, onMounted, ref } from 'vue'
```

- [ ] **Step 2: Wait for DOM mount before dashboard chart initialization**

After these state updates:

```ts
stats.value.totalPlans = completedPlans.length
stats.value.optimizedDistance = totalDistance.toFixed(1)
```

insert:

```ts
await nextTick()
```

This ensures the `v-else-if="!loadError"` chart block has mounted before checking:

```ts
if (chartRef.value && completedPlans.length > 0) { ... }
if (courierChartRef.value && rankRes.data.length > 0) { ... }
```

- [ ] **Step 3: Run the dashboard regression test**

Run:
```bash
cd frontend && npm run test:unit -- PageFeedback
```

Expected:
- dashboard chart initialization test now passes
- analytics and route history regression tests may still fail until their fixes land

- [ ] **Step 4: Commit**

```bash
git add frontend/src/views/Dashboard.vue frontend/src/__tests__/PageFeedback.spec.ts
git commit -m "fix: initialize dashboard charts after DOM mount"
```

### Task 3: Fix Analytics Chart Initialization Timing

**Files:**
- Modify: `frontend/src/views/Analytics.vue`
- Test: `frontend/src/__tests__/PageFeedback.spec.ts`

- [ ] **Step 1: Import `nextTick` in `frontend/src/views/Analytics.vue`**

Change:

```ts
import { computed, onMounted, ref } from 'vue'
```

To:

```ts
import { computed, nextTick, onMounted, ref } from 'vue'
```

- [ ] **Step 2: Wait for DOM mount after summary state is updated**

After:

```ts
summary.value = buildAnalyticsSummary({ plans, packages, couriers })
```

insert:

```ts
await nextTick()
```

before calling:

```ts
initTrendChart(plans)
initCourierChart(latestRanking)
initPackageStatusChart(packages)
initCourierStatusChart(couriers)
```

This is required because the chart sections are conditionally rendered from:

```ts
summary.value.factual.totalPlans
```

- [ ] **Step 3: Keep chart initialization guarded by actual visible sections**

If necessary, refine the calls so the code only initializes charts for sections currently rendered. For example:

```ts
if (summary.value.factual.totalPlans > 0) {
  initTrendChart(plans)
  initCourierChart(latestRanking)
  initPackageStatusChart(packages)
  initCourierStatusChart(couriers)
}
```

Only do this if the current template guarantees these charts are hidden when `totalPlans === 0`.

- [ ] **Step 4: Run the analytics regression test**

Run:
```bash
cd frontend && npm run test:unit -- PageFeedback
```

Expected:
- analytics success-state chart-init assertion passes
- prior dashboard assertions remain green

- [ ] **Step 5: Commit**

```bash
git add frontend/src/views/Analytics.vue frontend/src/__tests__/PageFeedback.spec.ts
git commit -m "fix: initialize analytics charts after DOM mount"
```

### Task 4: Fix Route History Trend Chart Initialization Timing

**Files:**
- Modify: `frontend/src/views/RouteHistory.vue`
- Test: `frontend/src/__tests__/RouteHistory.spec.ts`

- [ ] **Step 1: Import `nextTick` in `frontend/src/views/RouteHistory.vue`**

Change:

```ts
import { ref, onMounted, onBeforeUnmount, watch, computed } from 'vue'
```

To:

```ts
import { ref, onMounted, onBeforeUnmount, watch, computed, nextTick } from 'vue'
```

- [ ] **Step 2: Wait for DOM mount after `plans.value` is assigned**

In `loadPlans()`:

```ts
plans.value = getCompletedPlans(res.data)
```

then add:

```ts
await nextTick()
```

before:

```ts
if (plans.value.length > 0) {
  initTrendChart()
}
```

- [ ] **Step 3: Verify compare-mode behavior is unchanged**

Do not alter the existing:

```ts
watch(selectedPlans, () => {
  if (selectedPlans.value.length >= 2) {
    setTimeout(() => initCompareChart(), 100)
  }
})
```

That path is separate from the initial blank-chart regression. Leave it unchanged unless it is proven broken by a failing test.

- [ ] **Step 4: Run the route history regression suite**

Run:
```bash
cd frontend && npm run test:unit -- RouteHistory
```

Expected:
- empty-state tests still pass
- new trend-chart initialization test passes

- [ ] **Step 5: Commit**

```bash
git add frontend/src/views/RouteHistory.vue frontend/src/__tests__/RouteHistory.spec.ts
git commit -m "fix: initialize route history charts after DOM mount"
```

### Task 5: Full Verification And Manual QA

**Files:**
- Verify only

- [ ] **Step 1: Run the targeted chart-related tests**

Run:
```bash
cd frontend && npm run test:unit -- PageFeedback RouteHistory
```

Expected:
- all targeted regression tests pass

- [ ] **Step 2: Run the full frontend unit suite**

Run:
```bash
cd frontend && npm run test:unit
```

Expected:
- all unit tests pass

- [ ] **Step 3: Run the production build**

Run:
```bash
cd frontend && npm run build
```

Expected:
- build succeeds

- [ ] **Step 4: Manual browser verification**

Check the following with real completed-plan data:

1. `Dashboard.vue`
   - “最近调度记录” is visible
   - “最近工作量排行” is visible
2. `Analytics.vue`
   - “最近调度趋势” is visible
   - “最新调度工作量” is visible
   - status distribution charts are visible when history exists
3. `RouteHistory.vue`
   - “历史调度趋势” is visible on first load without requiring interaction

- [ ] **Step 5: Final commit**

```bash
git add frontend/src/views/Dashboard.vue frontend/src/views/Analytics.vue frontend/src/views/RouteHistory.vue frontend/src/__tests__/PageFeedback.spec.ts frontend/src/__tests__/RouteHistory.spec.ts
git commit -m "fix: render charts after conditional sections mount"
```

## Definition of Done

- Dashboard charts no longer appear blank when completed plans exist.
- Analytics charts no longer appear blank when completed plans exist.
- Route history trend chart no longer appears blank on initial load.
- Regression tests explicitly fail if `echarts.init(...)` is skipped again in these success paths.
- `npm run test:unit` passes.
- `npm run build` passes.

## Notes For The Implementer

- This is a timing bug, so treat `nextTick()` as the first-line fix unless evidence proves otherwise.
- Keep the fix page-local. A shared chart helper is unnecessary unless a second refactor is justified after the regression is resolved.
- Do not weaken the empty-state behavior to force the chart nodes into the DOM. The conditional rendering is correct; the initialization timing is not.
