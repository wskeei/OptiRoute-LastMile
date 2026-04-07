# Thesis Figure 4.5 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a standalone frontend preview page for thesis Figure 4.5 that renders a clean UML-style dispatch sequence diagram.

**Architecture:** Add a shell-less Vue route for the figure page, then render the sequence diagram with fixed-position SVG lines and lightweight semantic HTML overlays for participant headers, activation bars, loop/alt fragments, and the right-side legend. Keep the layout paper-oriented: left main sequence area, right legend column, short message labels only, and consistent orthogonal arrows.

**Tech Stack:** Vue 3, Vue Router 4, Vite, Vitest, scoped CSS, inline SVG

---

### Task 1: Add route and shell-less rendering for thesis figure pages

**Files:**
- Modify: `frontend/src/router/index.ts`
- Modify: `frontend/src/App.vue`
- Test: `frontend/src/__tests__/ThesisFigure45Route.spec.ts`

- [ ] **Step 1: Write the failing test**

```ts
import { describe, expect, it } from 'vitest'

import router from '../router'

describe('thesis figure 4.5 route', () => {
  it('registers a public shell-less route', () => {
    const route = router.getRoutes().find((item) => item.path === '/thesis/figure-4-5')

    expect(route).toBeTruthy()
    expect(route?.meta.requiresAuth).toBe(false)
    expect(route?.meta.shell).toBe(false)
  })
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm run test:unit -- src/__tests__/ThesisFigure45Route.spec.ts`
Expected: FAIL because the route does not exist yet.

- [ ] **Step 3: Write minimal implementation**

```ts
{
  path: '/thesis/figure-4-5',
  name: 'ThesisFigure45',
  component: () => import('../views/ThesisFigure45.vue'),
  meta: { requiresAuth: false, shell: false }
}
```

```ts
const isAuthPage = computed(
  () => route.path === '/login' || route.path === '/register' || route.meta.shell === false
)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npm run test:unit -- src/__tests__/ThesisFigure45Route.spec.ts`
Expected: PASS

### Task 2: Render the sequence diagram structure

**Files:**
- Create: `frontend/src/views/ThesisFigure45.vue`
- Test: `frontend/src/__tests__/ThesisFigure45.spec.ts`

- [ ] **Step 1: Write the failing test**

```ts
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import ThesisFigure45 from '../views/ThesisFigure45.vue'

describe('ThesisFigure45', () => {
  it('renders the required sequence participants, fragments, legend, and caption', () => {
    const wrapper = mount(ThesisFigure45)
    const text = wrapper.text()

    expect(text).toContain('前端页面（SmartDispatch）')
    expect(text).toContain('Dispatch API（FastAPI）')
    expect(text).toContain('DispatchService / BackgroundTasks')
    expect(text).toContain('Algorithm Module（K-Means + GA）')
    expect(text).toContain('SQLite Database')
    expect(text).toContain('loop every 1s')
    expect(text).toContain('loop each cluster')
    expect(text).toContain('loop generation')
    expect(text).toContain('alt 无包裹或无快递员')
    expect(text).toContain('消息缩写说明')
    expect(text).toContain('状态变化说明')
    expect(text).toContain('图4.5 调度时序图')
  })
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm run test:unit -- src/__tests__/ThesisFigure45.spec.ts`
Expected: FAIL because the view does not exist yet.

- [ ] **Step 3: Write minimal implementation**

```vue
<template>
  <main class="thesis-figure-page">
    <figure>
      <div>前端页面（SmartDispatch）</div>
      <figcaption>图4.5 调度时序图</figcaption>
    </figure>
  </main>
</template>
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npm run test:unit -- src/__tests__/ThesisFigure45.spec.ts`
Expected: PASS

### Task 3: Verify focused tests and production build

**Files:**
- Test: `frontend/src/__tests__/ThesisFigure45Route.spec.ts`
- Test: `frontend/src/__tests__/ThesisFigure45.spec.ts`

- [ ] **Step 1: Run focused tests**

Run: `npm run test:unit -- src/__tests__/ThesisFigure45Route.spec.ts src/__tests__/ThesisFigure45.spec.ts`
Expected: PASS with all suites green.

- [ ] **Step 2: Run build verification**

Run: `npm run build`
Expected: Vite build succeeds with exit code 0.
