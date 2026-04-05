# Courier Details Drawer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the couriers page so each courier card shows richer summary data and opens a right-side detail drawer with courier information.

**Architecture:** Keep the existing `CourierWork.vue` page as the single UI surface. Reuse the existing `/api/v1/delivery/couriers` list response, derive a lightweight station label locally, and add one selected-courier state to drive the drawer. Validate the new behaviors with legacy page tests before implementation.

**Tech Stack:** Vue 3 SFCs, Element Plus components, Vitest, Vue Test Utils, Axios

---

### Task 1: Lock in the new courier summary and drawer behavior

**Files:**
- Modify: `frontend/src/__tests__/LegacyPages.spec.ts`
- Test: `frontend/src/__tests__/LegacyPages.spec.ts`

- [ ] **Step 1: Write the failing tests**

```ts
it('shows richer courier summary data in each card', async () => {
  vi.mocked(axios.get).mockImplementation(async (url) => {
    if (url === '/api/v1/delivery/stations/current') return { data: { id: 1, name: '人民广场配送站' } }
    if (url === '/api/v1/delivery/couriers') {
      return {
        data: [{ id: 1, name: '李雷', phone: '13800000000', status: 'AVAILABLE', max_capacity: 68, station_id: 1 }]
      }
    }
    return { data: [] }
  })
})

it('opens a right-side drawer with courier details when a card is selected', async () => {
  await wrapper.get('.courier-card').trigger('click')
  expect(wrapper.text()).toContain('快递员详情')
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm run test:unit -- src/__tests__/LegacyPages.spec.ts`
Expected: FAIL because `CourierWork.vue` does not yet render the new summary fields or drawer details.

- [ ] **Step 3: Write minimal implementation**

```ts
const selectedCourier = ref<CourierItem | null>(null)
const openCourierDetails = (courier: CourierItem) => {
  selectedCourier.value = courier
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npm run test:unit -- src/__tests__/LegacyPages.spec.ts`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add frontend/src/__tests__/LegacyPages.spec.ts frontend/src/views/CourierWork.vue
git commit -m "feat: add courier detail drawer"
```

### Task 2: Refine the courier card presentation within the existing design system

**Files:**
- Modify: `frontend/src/views/CourierWork.vue`
- Test: `frontend/src/__tests__/LegacyPages.spec.ts`

- [ ] **Step 1: Write the failing test**

```ts
expect(wrapper.text()).toContain('最大载重')
expect(wrapper.text()).toContain('所属站点')
expect(wrapper.text()).toContain('点击查看详情')
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm run test:unit -- src/__tests__/LegacyPages.spec.ts`
Expected: FAIL because the existing cards only show avatar, name, phone, and one status tag.

- [ ] **Step 3: Write minimal implementation**

```vue
<article class="courier-card" @click="openCourierDetails(courier)">
  <div class="courier-metrics">
    <div class="metric-chip">
      <span>最大载重</span>
      <strong>{{ courier.max_capacity }} kg</strong>
    </div>
  </div>
</article>
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npm run test:unit -- src/__tests__/LegacyPages.spec.ts`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add frontend/src/views/CourierWork.vue frontend/src/__tests__/LegacyPages.spec.ts
git commit -m "style: enrich courier roster cards"
```
