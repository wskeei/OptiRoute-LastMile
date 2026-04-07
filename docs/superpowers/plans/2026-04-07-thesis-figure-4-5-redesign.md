# Thesis Figure 4.5 Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild thesis Figure 4.5 into a cleaner, code-faithful sequence diagram that is easier to read in the paper.

**Architecture:** Keep the existing shell-less route, but replace the crowded sequence rendering with a reduced participant model, stage-based message compression, and a lighter legend. The diagram remains a fixed-position paper layout rendered by SVG lines plus semantic HTML overlays for participants, fragments, activations, labels, and caption.

**Tech Stack:** Vue 3, scoped CSS, inline SVG, Vitest, Vue Test Utils

---

### Task 1: Redefine the acceptance test around the redesigned diagram

**Files:**
- Modify: `frontend/src/__tests__/ThesisFigure45.spec.ts`

- [ ] **Step 1: Write the failing test**

```ts
expect(text).toContain('调度页面 SmartDispatch')
expect(text).toContain('后台调度任务')
expect(text).toContain('路径优化模块')
expect(text).toContain('loop 轮询')
expect(text).toContain('loop 优化迭代')
expect(text).toContain('alt 资源不足')
expect(text).toContain('真实对应说明')
expect(text).not.toContain('loop each cluster')
expect(text).not.toContain('loop generation')
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm run test:unit -- src/__tests__/ThesisFigure45.spec.ts`
Expected: FAIL because the current figure still uses the older participant and fragment structure.

- [ ] **Step 3: Write minimal implementation**

Update `ThesisFigure45.vue` so the rendered text matches the new structure and removes the old nested loop labels.

- [ ] **Step 4: Run test to verify it passes**

Run: `npm run test:unit -- src/__tests__/ThesisFigure45.spec.ts`
Expected: PASS

### Task 2: Rebuild the figure layout to match the approved redesign

**Files:**
- Modify: `frontend/src/views/ThesisFigure45.vue`

- [ ] **Step 1: Replace the participant model**

Use five participants only:

```ts
'调度页面 SmartDispatch'
'Dispatch API'
'后台调度任务'
'路径优化模块'
'SQLite'
```

- [ ] **Step 2: Compress the message model**

Use a stage-based message set with around 10-11 labels:

```ts
'发起调度'
'创建 plan'
'返回 plan_id'
'启动后台任务'
'读取待调度数据'
'资源不足则结束'
'执行聚类'
'预建路线'
'执行路径优化'
'写中间进度'
'轮询状态'
'查询 plan/routes'
'返回状态与路线'
'写最终结果'
```

- [ ] **Step 3: Reduce fragment nesting**

Keep only:

```ts
'loop 轮询'
'loop 优化迭代'
'alt 资源不足'
```

Remove the older nested:

```ts
'loop each cluster'
'loop generation'
```

- [ ] **Step 4: Simplify the right-side legend**

Keep one narrow explanation area with:

```ts
'真实对应说明'
'状态'
'plan: OPTIMIZING -> READY / COMPLETED'
'route: calculating -> optimizing -> optimized'
```

- [ ] **Step 5: Rebalance spacing and styling**

Adjust fixed coordinates so:

- message labels do not overlap fragments
- the legend stays visually secondary
- activation bars remain sparse and consistent
- the caption remains detached from the main figure

### Task 3: Verify focused tests and production build

**Files:**
- Modify: `frontend/src/__tests__/ThesisFigure45.spec.ts`
- Modify: `frontend/src/views/ThesisFigure45.vue`

- [ ] **Step 1: Run focused tests**

Run: `npm run test:unit -- src/__tests__/ThesisFigure45Route.spec.ts src/__tests__/ThesisFigure45.spec.ts`
Expected: PASS with all suites green.

- [ ] **Step 2: Run build verification**

Run: `npm run build`
Expected: Vite build succeeds with exit code 0.
