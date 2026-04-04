# Frontend Content Simplification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reduce text density, visual noise, and duplicated explanation across the frontend so the UI feels calmer, more task-first, and easier to scan.

**Architecture:** Keep the current Vue 3 + Element Plus page structure and route map, but shift the interface from explanation-led screens to action-led screens. Consolidate repeated "demo system" narration into a smaller number of surfaces, simplify navigation and hero sections, and normalize old glass-card pages onto the newer restrained visual language already present in dashboard and auth.

**Tech Stack:** Vue 3, TypeScript, Vue Router, Pinia, Element Plus, Leaflet, ECharts, Vite, Vitest

---

## Scope Baseline

- This plan is derived from the 2026-04-04 design critique and focuses only on frontend simplification, not backend behavior changes.
- Use a calm operational tone:
  - fewer explanations
  - fewer simultaneous warnings
  - one primary action per screen
  - secondary facts disclosed only when needed
- Preserve the current truthful product direction:
  - demo environment remains explicit
  - estimated metrics remain labeled
  - core route stays `/dispatch`

## Success Criteria

- Users can identify the primary action on each page within 2 seconds.
- No page opens with more than one persistent explanatory block above the main task area.
- Navigation remains readable without two-line descriptions on every item.
- Route history cards and analytics cards surface only the minimum needed to decide where to click next.
- Legacy pages no longer feel like a separate visual system.

## File Map

- Modify: `frontend/src/lib/ux.ts`
  - shorten navigation copy
  - shorten onboarding copy
  - centralize concise demo/truth labels
- Modify: `frontend/src/App.vue`
  - reduce sidebar narration
  - simplify primary/secondary nav presentation
  - remove redundant mobile summary copy
- Modify: `frontend/src/style.css`
  - add shared subdued text/surface tokens
  - align common card/header spacing
- Modify: `frontend/src/views/Dashboard.vue`
  - simplify hero, onboarding, metrics, and chart intros
- Modify: `frontend/src/views/SmartDispatch.vue`
  - prioritize dispatch controls and result area over explanation
- Modify: `frontend/src/views/Analytics.vue`
  - compress factual/estimate framing
  - demote repetitive captions
- Modify: `frontend/src/views/RouteHistory.vue`
  - reduce card-level metrics
  - move secondary metrics to detail drawer
- Modify: `frontend/src/views/Settings.vue`
  - merge overlapping explanation blocks
  - reduce copy around maintenance actions
- Modify: `frontend/src/views/PackageFlow.vue`
  - remove bulky demo narration
  - normalize header and table framing
- Modify: `frontend/src/views/CourierWork.vue`
  - remove emoji-led hierarchy
  - normalize to shared page shell
- Modify: `frontend/src/views/RealtimeMap.vue`
  - simplify top panel and status messaging
- Modify: `frontend/src/views/Login.vue`
- Modify: `frontend/src/views/Register.vue`
  - keep auth as the visual baseline for restraint
- Modify: `frontend/src/__tests__/ux-config.spec.ts`
  - keep navigation and onboarding expectations aligned with shorter copy
- Create: `frontend/src/__tests__/AppShell.spec.ts`
  - verify global shell no longer renders redundant summary copy
  - verify compact nav still exposes core routes
- Modify: `frontend/src/__tests__/PageFeedback.spec.ts`
  - keep dashboard/analytics actionable after copy reduction
- Modify: `frontend/src/__tests__/RouteHistory.spec.ts`
  - keep empty state actionable after list simplification

## Implementation Rules

- Do not add new pages or routes.
- Do not solve content overload by hiding critical actions behind extra clicks.
- Do not keep the same explanatory sentence in sidebar, hero, alert, and card body simultaneously.
- Prefer:
  - short labels
  - conditional help
  - inline badges
  - drawer/detail disclosure
- Avoid:
  - emoji headings
  - duplicated glass-card styles
  - stacked hero + alert + instructions + checklist when one of them can carry the guidance

### Task 1: Reduce Global Narration and Navigation Noise

**Files:**
- Modify: `frontend/src/lib/ux.ts`
- Modify: `frontend/src/App.vue`
- Modify: `frontend/src/style.css`
- Modify: `frontend/src/__tests__/ux-config.spec.ts`
- Create: `frontend/src/__tests__/AppShell.spec.ts`

- [ ] **Step 1: Shorten the shared UX copy in `frontend/src/lib/ux.ts`**

Target outcomes:
- `NAV_ITEMS[].label` stays task-first and short
- `NAV_ITEMS[].description` becomes optional supporting copy, not mandatory permanent copy
- `ONBOARDING_STEPS[].description` is trimmed to one short clause each
- add one concise environment label for reuse, instead of repeating long demo disclaimers page by page

Suggested target direction:
- `调度中心`: keep
- `路线监控`: keep
- `调度历史`: keep
- `任务概览`: keep
- descriptions shortened from sentences to short fragments such as `发起调度`, `查看结果`, `复盘记录`

- [ ] **Step 2: Simplify the sidebar in `frontend/src/App.vue`**

Required changes:
- remove the persistent sidebar summary block at [App.vue:27](/Users/zeiy/Project/OptiRoute-LastMile/frontend/src/App.vue#L27)
- remove the mobile fallback summary block at [App.vue:106](/Users/zeiy/Project/OptiRoute-LastMile/frontend/src/App.vue#L106)
- show one-line nav labels by default
- only show nav descriptions when one of these is true:
  - the item is active
  - the screen is wide and the design still needs a secondary cue
- keep "更多页面" behavior, but reduce its description copy

- [ ] **Step 3: Normalize shared shell styling in `frontend/src/style.css`**

Required changes:
- introduce shared muted text tokens for captions/help text
- reduce visual contrast between nav label and nav description
- align card padding and section spacing to a calmer baseline
- keep primary actions visible without increasing saturation

- [ ] **Step 4: Add/adjust shell tests**

Run after implementation:
- create `frontend/src/__tests__/AppShell.spec.ts`
- assert the shell no longer renders the removed summary sentence
- assert core routes still render in primary navigation
- update `frontend/src/__tests__/ux-config.spec.ts` if onboarding or nav copy constants change

- [ ] **Step 5: Verify Task 1**

Run:
```bash
cd frontend && npm run test:unit -- AppShell ux-config
```

Expected:
- shell tests pass
- navigation order is unchanged
- no test asserts the removed summary copy

- [ ] **Step 6: Commit**

```bash
git add frontend/src/lib/ux.ts frontend/src/App.vue frontend/src/style.css frontend/src/__tests__/ux-config.spec.ts frontend/src/__tests__/AppShell.spec.ts
git commit -m "refactor: reduce global navigation narration"
```

### Task 2: Simplify Dashboard and Dispatch Into Clear Action Screens

**Files:**
- Modify: `frontend/src/views/Dashboard.vue`
- Modify: `frontend/src/views/SmartDispatch.vue`
- Modify: `frontend/src/lib/ux.ts`
- Modify: `frontend/src/__tests__/PageFeedback.spec.ts`

- [ ] **Step 1: Rewrite the dashboard hero and top-of-page structure**

Required changes for [Dashboard.vue:3](/Users/zeiy/Project/OptiRoute-LastMile/frontend/src/views/Dashboard.vue#L3):
- keep one short headline
- reduce `page-summary` to one sentence max
- replace the standalone info alert with either:
  - a compact environment badge in the hero, or
  - a short inline note attached to the main CTA
- do not keep both a long hero summary and a full-width explanatory alert unless an error/loading state is active

- [ ] **Step 2: Reduce dashboard duplication below the hero**

Required changes:
- keep only one onboarding surface:
  - either a compact 3-step checklist
  - or the "关键入口" links
- do not show both as two equally weighted cards unless one is significantly compressed
- metric cards should keep:
  - short label
  - number
  - optional micro-caption only where meaning would otherwise be unclear
- chart section intros should be shortened to fragments, not full explanatory sentences

- [ ] **Step 3: Rebalance the dispatch page around the main controls**

Required changes for [SmartDispatch.vue:3](/Users/zeiy/Project/OptiRoute-LastMile/frontend/src/views/SmartDispatch.vue#L3):
- keep the two hero buttons as the dominant focus
- reduce hero text to one sentence
- convert the full-width demo alert at [SmartDispatch.vue:22](/Users/zeiy/Project/OptiRoute-LastMile/frontend/src/views/SmartDispatch.vue#L22) into a compact note or badge near the controls
- keep `DISPATCH_TRUTH_NOTES`, but move them behind a lighter disclosure pattern:
  - collapsible note block
  - popover
  - secondary details area
- remove the separate "下一步怎么做" panel if the same onboarding sequence is already taught clearly elsewhere, or collapse it into a smaller helper card shown only when `!canDispatch`

- [ ] **Step 4: Preserve persistent feedback while reducing noise**

Update `frontend/src/__tests__/PageFeedback.spec.ts` as needed so the tests still verify:
- dashboard error remains visible inline
- analytics error remains visible inline

Do not remove actionable empty/error states to achieve visual simplicity.

- [ ] **Step 5: Verify Task 2**

Run:
```bash
cd frontend && npm run test:unit -- PageFeedback
```

Manual check:
- dashboard first screen shows one clear CTA
- dispatch first screen shows buttons first, explanation second
- no page begins with hero + info alert + checklist all competing at once

- [ ] **Step 6: Commit**

```bash
git add frontend/src/views/Dashboard.vue frontend/src/views/SmartDispatch.vue frontend/src/lib/ux.ts frontend/src/__tests__/PageFeedback.spec.ts
git commit -m "refactor: simplify dashboard and dispatch content hierarchy"
```

### Task 3: Compress Explanation-Heavy Analysis and History Screens

**Files:**
- Modify: `frontend/src/views/Analytics.vue`
- Modify: `frontend/src/views/RouteHistory.vue`
- Modify: `frontend/src/views/Settings.vue`
- Modify: `frontend/src/__tests__/RouteHistory.spec.ts`

- [ ] **Step 1: Simplify analytics framing**

Required changes for [Analytics.vue:3](/Users/zeiy/Project/OptiRoute-LastMile/frontend/src/views/Analytics.vue#L3):
- shorten hero text
- keep the "estimate" caveat, but avoid presenting it as a full-width warning block plus a second explanatory paragraph plus per-card captions
- use concise section labels such as:
  - `实际数据`
  - `演示估算`
- reduce KPI captions to only the ones users genuinely need to interpret the number

- [ ] **Step 2: Reduce density in history list cards**

Required changes for [RouteHistory.vue:44](/Users/zeiy/Project/OptiRoute-LastMile/frontend/src/views/RouteHistory.vue#L44):
- show only 3 primary card metrics in list view:
  - package count
  - route count
  - total distance
- move average distance, total weight, and algorithm parameters into the drawer or compare mode
- keep one obvious action per card: `查看复盘`

- [ ] **Step 3: Merge overlapping explanation in settings**

Required changes for [Settings.vue:13](/Users/zeiy/Project/OptiRoute-LastMile/frontend/src/views/Settings.vue#L13):
- merge `调度运行方式` and `演示范围说明` if they remain semantically close after trimming
- shorten maintenance action descriptions to one line each
- avoid a page where every card starts with title + paragraph + bullet list unless that text directly changes the next action

- [ ] **Step 4: Keep the history empty state actionable**

Update `frontend/src/__tests__/RouteHistory.spec.ts` if needed, but preserve:
- explicit no-history title
- concrete next step
- link back to `/dispatch`

- [ ] **Step 5: Verify Task 3**

Run:
```bash
cd frontend && npm run test:unit -- RouteHistory
```

Manual check:
- analytics reads like a dashboard, not a policy memo
- history cards are scannable in a quick vertical pass
- settings no longer contains two cards that explain nearly the same thing

- [ ] **Step 6: Commit**

```bash
git add frontend/src/views/Analytics.vue frontend/src/views/RouteHistory.vue frontend/src/views/Settings.vue frontend/src/__tests__/RouteHistory.spec.ts
git commit -m "refactor: compress analysis and history page copy"
```

### Task 4: Normalize Legacy Pages to the Quieter System

**Files:**
- Modify: `frontend/src/views/PackageFlow.vue`
- Modify: `frontend/src/views/CourierWork.vue`
- Modify: `frontend/src/views/RealtimeMap.vue`
- Modify: `frontend/src/style.css`

- [ ] **Step 1: Bring `PackageFlow.vue` onto the shared page structure**

Required changes:
- replace the old local `glass-card` framing at [PackageFlow.vue:2](/Users/zeiy/Project/OptiRoute-LastMile/frontend/src/views/PackageFlow.vue#L2) with the same shell/header conventions used by dashboard/settings
- shorten the header note to one sentence or a compact badge
- keep the table note only if users genuinely need it to understand the data source
- reduce dialog helper copy to a short hint near the submit action instead of a paragraph above the form

- [ ] **Step 2: Rebuild `CourierWork.vue` as a restrained operational page**

Required changes:
- remove emoji from heading at [CourierWork.vue:4](/Users/zeiy/Project/OptiRoute-LastMile/frontend/src/views/CourierWork.vue#L4)
- adopt `page-shell` + `section-card`
- reduce card chrome so courier cards rely on spacing and typography more than shadows
- if the page remains sparse, add a short empty/state intro rather than decorative styling

- [ ] **Step 3: Simplify the map page header and status treatment**

Required changes for [RealtimeMap.vue:3](/Users/zeiy/Project/OptiRoute-LastMile/frontend/src/views/RealtimeMap.vue#L3):
- make the top panel one compact control bar
- keep `statusMessage`, but avoid the page feeling like header + alert + giant map + separate info card all with equal weight
- reduce duplicate wording between panel copy and alert copy
- if no route exists, let the status panel carry the instruction instead of stacking multiple explanations

- [ ] **Step 4: Remove duplicated local glass-card definitions**

Required changes:
- where these pages duplicate `.glass-card` styles locally, replace them with shared tokens or shared class behavior from `frontend/src/style.css`
- leave page-specific layout rules in component styles, but move visual-system decisions to the shared stylesheet

- [ ] **Step 5: Verify Task 4**

Manual check:
- `PackageFlow`, `CourierWork`, and `RealtimeMap` now look like part of the same product as dashboard/settings
- no emoji headings remain
- no page uses a stronger card/shadow language than the primary dispatch flow

- [ ] **Step 6: Commit**

```bash
git add frontend/src/views/PackageFlow.vue frontend/src/views/CourierWork.vue frontend/src/views/RealtimeMap.vue frontend/src/style.css
git commit -m "refactor: normalize legacy pages to quieter visual system"
```

### Task 5: Keep Auth Minimal and Run Final Verification

**Files:**
- Modify: `frontend/src/views/Login.vue`
- Modify: `frontend/src/views/Register.vue`
- Modify: `frontend/src/style.css`

- [ ] **Step 1: Trim auth copy to the minimum useful set**

Required changes:
- keep small eyebrow, page title, and one short support sentence
- shorten CTA labels if they feel verbose after the rest of the product is simplified
- preserve explicit field labels and inline error states

- [ ] **Step 2: Align auth spacing and tone with the quieter app shell**

Required changes:
- keep auth pages restrained and neutral
- do not introduce decorative gradients or louder accents than the main app
- use auth as the quality bar for concise copy and uncluttered hierarchy

- [ ] **Step 3: Run full verification**

Run:
```bash
cd frontend && npm run test:unit
```

Run:
```bash
cd frontend && npm run build
```

Manual QA checklist:
- login and register still show visible labels and inline status
- sidebar is faster to scan than before
- dashboard and dispatch each expose one clear next action
- analytics, settings, and history no longer read like documentation pages
- package, courier, and monitor pages no longer feel like a separate older design system
- no critical explanatory truth note was lost during simplification

- [ ] **Step 4: Commit**

```bash
git add frontend/src/views/Login.vue frontend/src/views/Register.vue frontend/src/style.css
git commit -m "polish: finalize simplified frontend copy and hierarchy"
```

## Definition of Done

- The app keeps its current truthful demo positioning, but stops repeating it everywhere.
- Text is shorter, but not less clear.
- Navigation and cards are scannable without reading full sentences.
- Primary pages feel calmer and more intentional.
- Old glass-card pages are visually aligned with the newer restrained pages.
- `npm run test:unit` passes.
- `npm run build` passes.

## Recommended Execution Order

1. Task 1: global shell and copy guardrails
2. Task 2: dashboard and dispatch
3. Task 3: analytics, history, settings
4. Task 4: legacy page normalization
5. Task 5: auth pass and final verification

## Notes for the Implementer

- If a screen becomes ambiguous after copy removal, add back one short instruction near the action rather than restoring a large descriptive block.
- Prefer moving secondary detail into:
  - drawer content
  - collapse panels
  - tooltips
  - conditional empty states
- When forced to choose between "fully explained" and "instantly scannable", choose scannable first, then re-add only the minimum explanation that prevents a real mistake.
