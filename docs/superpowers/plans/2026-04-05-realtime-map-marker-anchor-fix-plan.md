# Realtime Map Marker Anchor And Sidebar Collapse Fix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the realtime map marker misalignment on zoom and restore proper desktop sidebar collapse behavior by correcting the underlying geometry and layout models instead of relying on visual-only hacks.

**Architecture:** There are two UI-geometry bugs here. The map issue is a marker-rendering bug in `RealtimeMap.vue`, not a backend coordinate bug, and should be fixed by giving Leaflet explicit icon dimensions and anchors. The sidebar issue is a layout bug in `App.vue`: the collapsed state hides copy but does not change the grid column width, so the desktop shell never truly collapses. Fix both with explicit geometry/layout rules and regression tests.

**Tech Stack:** Vue 3, TypeScript, Leaflet, Vue Test Utils, Vitest, Vite

---

## Debug Baseline

- Root cause already identified:
  - courier markers in `RealtimeMap.vue` use `L.divIcon(...)`
  - the icon is created with `iconSize: [0, 0]`
  - the anchor is `iconAnchor: [0, 0]`
  - the visible marker is then moved with CSS using absolute positioning and `transform: translate(-50%, -50%)`
  - Leaflet only reprojects the actual icon box and anchor, not the CSS illusion layered outside that box
  - result: markers visually drift / appear fixed during zoom because the anchor model and visible marker geometry do not match
- This affects:
  - courier markers on `frontend/src/views/RealtimeMap.vue`
- Likely also worth normalizing:
  - package number markers in the same file, so both marker types follow the same anchor rules
- Additional issue identified:
  - desktop sidebar collapse in `frontend/src/App.vue` is only a content hide/show state
  - the shell grid remains `18rem minmax(0, 1fr)` even when `collapsed === true`
  - result: the sidebar looks “not properly collapsed” because width never shrinks

## File Map

- Modify: `frontend/src/views/RealtimeMap.vue`
  - replace zero-size courier icon geometry with explicit icon size and anchor
  - remove the CSS positioning hack that compensates for the broken anchor model
  - optionally normalize numbered package markers to explicit anchor values
- Modify: `frontend/src/__tests__/RealtimeMap.spec.ts`
  - add regression tests asserting courier markers are created with real `iconSize` and a centered `iconAnchor`
  - add regression tests asserting package markers also use explicit icon sizing / anchoring
- Modify: `frontend/src/App.vue`
  - make desktop sidebar collapse actually reduce layout width
  - keep mobile behavior unchanged
- Modify: `frontend/src/__tests__/AppShell.spec.ts`
  - add regression coverage for desktop collapsed layout behavior

## Implementation Rules

- Do not change route coordinates or simulation progression logic.
- Do not “fix” this with manual event listeners on zoom or repeated `setLatLng()` calls during zoom.
- Do not keep `iconSize: [0, 0]` for visible markers.
- Do not rely on `position: absolute` + transform to center the whole marker around a zero-size box.
- Prefer:
  - explicit `iconSize`
  - explicit `iconAnchor`
  - minimal CSS on the marker content itself
  - one marker geometry model that Leaflet fully understands
  - explicit collapsed width for the desktop shell
  - a class or attribute on the shell that lets layout respond to collapsed state

### Task 1: Add Failing Regression Tests For Marker Geometry

**Files:**
- Modify: `frontend/src/__tests__/RealtimeMap.spec.ts`

- [ ] **Step 1: Write a failing test for courier marker icon geometry**

Add a test in `frontend/src/__tests__/RealtimeMap.spec.ts` that:
- mocks one completed plan with at least one courier route
- mounts `RealtimeMap.vue`
- waits for `flushPromises()`
- inspects `L.divIcon` calls
- asserts the courier marker icon is created with:
  - non-zero `iconSize`
  - centered `iconAnchor` matching the visible geometry

Suggested assertion direction:

```ts
expect(L.divIcon).toHaveBeenCalledWith(
  expect.objectContaining({
    iconSize: [expect.any(Number), expect.any(Number)],
    iconAnchor: [expect.any(Number), expect.any(Number)]
  })
)
```

Then refine it to check for the actual intended dimensions.

- [ ] **Step 2: Run the realtime map test and confirm it fails**

Run:
```bash
cd frontend && npm run test:unit -- RealtimeMap
```

Expected:
- the new geometry assertion fails because the current courier marker uses `[0, 0]` for both size and anchor

- [ ] **Step 3: Write a failing test for numbered package marker geometry**

In the same test file, add a second assertion or test that the package number marker icon also has:
- explicit `iconSize`
- explicit `iconAnchor`

This keeps both marker systems aligned and prevents future regressions where only one marker type is fixed.

- [ ] **Step 4: Re-run the targeted suite and confirm failure**

Run:
```bash
cd frontend && npm run test:unit -- RealtimeMap
```

Expected:
- at least one geometry assertion fails before implementation

- [ ] **Step 5: Commit**

```bash
git add frontend/src/__tests__/RealtimeMap.spec.ts
git commit -m "test: add realtime map marker anchor regression coverage"
```

### Task 2: Fix Courier Marker Anchor Geometry

**Files:**
- Modify: `frontend/src/views/RealtimeMap.vue`
- Test: `frontend/src/__tests__/RealtimeMap.spec.ts`

- [ ] **Step 1: Replace the broken courier `divIcon` geometry**

In `drawCouriers()`, change the courier icon creation from:

```ts
iconSize: [0, 0],
iconAnchor: [0, 0]
```

to a real visual box with explicit geometry, for example:

```ts
iconSize: [96, 32],
iconAnchor: [48, 16]
```

The exact dimensions can differ, but they must match the rendered content well enough that Leaflet owns the positioning model.

- [ ] **Step 2: Remove the CSS centering hack**

In the scoped styles for `.courier-marker-inner`, remove the geometry workaround:

```css
position: absolute;
top: 0;
left: 0;
transform: translate(-50%, -50%);
```

Keep only visual styling that does not fight Leaflet’s marker projection.

- [ ] **Step 3: Preserve hover behavior without breaking anchor math**

If hover scale is kept, make sure it scales from the center of the marker instead of reintroducing offset hacks.

Example direction:

```css
transform-origin: center;
```

If needed, move hover styling to a subtle scale or shadow change that does not visually shift the marker off its anchor.

- [ ] **Step 4: Run the courier marker regression test**

Run:
```bash
cd frontend && npm run test:unit -- RealtimeMap
```

Expected:
- courier marker geometry assertions now pass
- existing “newest completed result” test still passes

- [ ] **Step 5: Commit**

```bash
git add frontend/src/views/RealtimeMap.vue frontend/src/__tests__/RealtimeMap.spec.ts
git commit -m "fix: align realtime courier markers with leaflet anchors"
```

### Task 3: Normalize Package Marker Anchors In The Same File

**Files:**
- Modify: `frontend/src/views/RealtimeMap.vue`
- Test: `frontend/src/__tests__/RealtimeMap.spec.ts`

- [ ] **Step 1: Give package number markers explicit anchor values**

In `drawRoutesAndPackages()`, the numbered package `divIcon` already has:

```ts
iconSize: [24, 24]
```

Add an explicit matching anchor, for example:

```ts
iconAnchor: [12, 12]
```

This ensures package markers and courier markers follow the same projection model.

- [ ] **Step 2: Keep popup behavior unchanged**

Do not alter:
- popup binding logic
- package ordering logic
- coordinate conversion logic

This task is only about icon geometry consistency.

- [ ] **Step 3: Run the package-marker regression assertions**

Run:
```bash
cd frontend && npm run test:unit -- RealtimeMap
```

Expected:
- package marker geometry assertions pass
- courier marker assertions remain green

- [ ] **Step 4: Commit**

```bash
git add frontend/src/views/RealtimeMap.vue frontend/src/__tests__/RealtimeMap.spec.ts
git commit -m "fix: normalize realtime package marker anchors"
```

### Task 4: Full Verification And Manual Map QA

**Files:**
- Verify only

- [ ] **Step 1: Run the targeted realtime map suite**

Run:
```bash
cd frontend && npm run test:unit -- RealtimeMap
```

Expected:
- all realtime map tests pass

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

Open the realtime map page with a plan that has visible route and courier markers, then verify:

1. Zoom in repeatedly:
   - courier markers stay attached to their route positions
   - numbered package markers stay centered on their coordinates
2. Zoom out repeatedly:
   - markers continue to align with the underlying route geometry
3. Pan the map:
   - markers move with the map tiles and route layers
4. Trigger `下一步` and `重置`:
   - courier markers still move correctly after simulation updates

- [ ] **Step 5: Final commit**

```bash
git add frontend/src/views/RealtimeMap.vue frontend/src/__tests__/RealtimeMap.spec.ts
git commit -m "fix: keep realtime map markers aligned during zoom"
```

### Task 5: Restore Proper Desktop Sidebar Collapse

**Files:**
- Modify: `frontend/src/App.vue`
- Modify: `frontend/src/__tests__/AppShell.spec.ts`

- [ ] **Step 1: Write a failing sidebar collapse regression test**

Add a test in `frontend/src/__tests__/AppShell.spec.ts` that:
- mounts `App.vue` in desktop mode (`window.innerWidth > 960`)
- clicks the sidebar toggle
- asserts the shell enters a real collapsed layout state instead of only hiding text

Preferred assertion directions:
- assert a collapsed class or data attribute appears on the shell container
- assert the sidebar element receives a collapsed modifier that changes width semantics

Example direction:

```ts
const toggle = wrapper.get('button.sidebar-toggle')
await toggle.trigger('click')

expect(wrapper.get('.app-shell').classes()).toContain('shell-collapsed')
```

The exact selector/class may differ, but the test must verify layout state, not just hidden copy.

- [ ] **Step 2: Run the app shell test and confirm it fails**

Run:
```bash
cd frontend && npm run test:unit -- AppShell
```

Expected:
- the new collapse-layout assertion fails before implementation

- [ ] **Step 3: Make `App.vue` expose a real collapsed layout state**

Current root cause:

```css
.app-shell {
  grid-template-columns: 18rem minmax(0, 1fr);
}
```

and `.sidebar.collapsed` only changes alignment, not width.

Implement a real desktop collapsed layout by:
- adding a class or state hook on `.app-shell`, for example `shell-collapsed`
- changing the desktop grid from `18rem` to a narrow collapsed width when collapsed, for example:

```css
.app-shell.shell-collapsed {
  grid-template-columns: 5.5rem minmax(0, 1fr);
}
```

- [ ] **Step 4: Keep the collapsed sidebar internally consistent**

When collapsed:
- brand mark should remain visible
- nav icons should remain centered
- hidden labels should not leave awkward spacing
- the desktop toggle should still be reachable

If needed, add targeted rules such as:
- narrower sidebar padding
- centered sidebar head layout
- collapsed `.brand` alignment adjustments

- [ ] **Step 5: Preserve mobile behavior**

Do not alter the existing mobile behavior where:
- `isCompactNavigation` hides the desktop toggle
- the shell becomes single-column at `max-width: 960px`

The collapse fix is for desktop layout only.

- [ ] **Step 6: Run the sidebar regression test**

Run:
```bash
cd frontend && npm run test:unit -- AppShell
```

Expected:
- the new collapse-layout test passes
- existing nav-visibility and removed-copy tests still pass

- [ ] **Step 7: Commit**

```bash
git add frontend/src/App.vue frontend/src/__tests__/AppShell.spec.ts
git commit -m "fix: restore proper desktop sidebar collapse"
```

### Task 6: Full Verification For Both Fixes

**Files:**
- Verify only

- [ ] **Step 1: Run the targeted suites**

Run:
```bash
cd frontend && npm run test:unit -- RealtimeMap AppShell
```

Expected:
- all realtime map and app shell tests pass

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

Check both feature areas:

1. Realtime map
   - zoom in/out: courier and package markers stay attached to coordinates
   - pan: markers move with tiles and route layers
   - simulation step/reset: courier markers still move correctly
2. Desktop sidebar
   - click collapse toggle
   - sidebar width actually shrinks to a narrow icon rail
   - main content area expands accordingly
   - click toggle again restores full width and labels

- [ ] **Step 5: Final commit**

```bash
git add frontend/src/views/RealtimeMap.vue frontend/src/__tests__/RealtimeMap.spec.ts frontend/src/App.vue frontend/src/__tests__/AppShell.spec.ts
git commit -m "fix: align map markers and restore sidebar collapse"
```

## Definition of Done

- Courier markers no longer drift or appear fixed during zoom.
- Package number markers use explicit anchor geometry as well.
- Desktop sidebar collapse reduces actual layout width instead of only hiding copy.
- `RealtimeMap.spec.ts` contains regression coverage for marker icon geometry.
- `AppShell.spec.ts` contains regression coverage for desktop collapsed layout state.
- `npm run test:unit` passes.
- `npm run build` passes.
- Manual zoom/pan verification confirms markers stay aligned with map coordinates.
- Manual desktop verification confirms the sidebar truly collapses and expands.

## Notes For The Implementer

- The key principle is: Leaflet must own the marker box and anchor.
- If the visible marker shape is larger than the `iconSize`, the bug will come back.
- Do not solve this with more CSS transforms unless the transform is purely decorative and does not redefine the marker’s actual position relative to its anchor.
- The key principle for the sidebar is similar: the shell layout must own the collapsed width. Hiding children without changing the grid column is not a real collapse.
