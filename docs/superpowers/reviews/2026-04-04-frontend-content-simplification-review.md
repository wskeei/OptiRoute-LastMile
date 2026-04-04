# Frontend Content Simplification Review

Date: 2026-04-04
Plan: `docs/superpowers/plans/2026-04-04-frontend-content-simplification-plan.md`
Reviewed branch/worktree: `refactor/frontend-content-simplification` in `.worktrees/refactor-frontend-content-simplification`
Base SHA: `17a3f8013b80de40bb94acc7f2b89aa7ec88e7ac`
Head SHA: `7c98fcb83d9f52357ed580ffe58412c67ada46b1`

## Scope

This review checks whether the implementation in `.worktrees/refactor-frontend-content-simplification` satisfies the simplification plan, with emphasis on:

- reduced text density and repeated explanation
- calmer, task-first hierarchy
- legacy page normalization
- responsive behavior after the simplification pass

## Findings

### P1: Courier add dialog is still fixed at `30%` width and becomes unusably narrow on mobile

Plan mismatch:

- Task 4 normalizes `CourierWork.vue` into the shared quieter system, but the dialog kept the old fixed width behavior.
- The simplification pass should not leave core actions less usable than before, especially on small screens.

Evidence:

- `frontend/src/views/CourierWork.vue:37`

Why this matters:

- On a 375px-wide phone, `30%` yields a dialog around 112px wide before padding, which is effectively unusable for a three-field form.
- This undermines the plan's product-grade usability goal and leaves one legacy page with desktop-only behavior.

Suggested fix:

- Replace the fixed `width="30%"` with the same responsive approach used in `PackageFlow.vue`, or use a `dialogWidth` reactive value with a mobile-safe fallback such as `90vw` / `min(32rem, calc(100vw - 2rem))`.

### P2: Realtime map still duplicates status feedback with toasts after moving messaging into the page header

Plan mismatch:

- Task 4 explicitly called for the status panel to carry the instruction instead of stacking multiple explanations.
- The page now has an inline status line, but it still fires transient `ElMessage.warning/error(...)` to repeat the same state.

Evidence:

- `frontend/src/views/RealtimeMap.vue:7`
- `frontend/src/views/RealtimeMap.vue:85`
- `frontend/src/views/RealtimeMap.vue:94`
- `frontend/src/views/RealtimeMap.vue:103`

Why this matters:

- The page remains noisier than intended: users get the same information in two channels.
- This weakens the "calm operational tone" requirement and makes the monitor page feel less simplified than the other refactored screens.

Suggested fix:

- Let `statusMessage` be the primary source of truth for no-plan / no-route / load-failed states.
- Reserve toasts for truly transient user-triggered actions, not initial page-load conditions.

### P2: Settings still front-loads all long-form truth notes in one always-open block

Plan mismatch:

- The implementation merged the two explanatory cards, but it did not meaningfully reduce the page's text density.
- The simplification plan aimed to reduce repeated explanation and prefer conditional disclosure for secondary detail.

Evidence:

- `frontend/src/views/Settings.vue:12`
- `frontend/src/views/Settings.vue:20`

Why this matters:

- The first non-hero section is still a large always-open documentation block with two subsection headings and six bullet items.
- This keeps the settings page reading like a policy memo instead of an action-first utility screen.

Suggested fix:

- Collapse the detail into disclosure sections, or replace the two bullet groups with short summaries and an explicit "展开说明" affordance.
- Keep the data overview and maintenance actions visually ahead of long-form explanation.

## Assumptions

- The responsive dialog finding assumes the courier add flow is expected to remain available on narrow screens, which is consistent with the broader simplification and normalization goals.
- The settings-page finding treats text-density reduction as a real requirement, not only a card-merging exercise.

## Verification Performed

- `cd .worktrees/refactor-frontend-content-simplification/frontend && npm run test:unit`
  - Result: passed, 7 test files and 22 tests passed.
- `cd .worktrees/refactor-frontend-content-simplification/frontend && npm run build`
  - Result: passed.
  - Note: build still reports large bundle warnings for ECharts / main chunks, but this review does not treat that as part of the simplification-plan acceptance criteria.

## Overall Assessment

The branch largely follows the plan:

- global navigation is quieter
- dashboard and dispatch are more task-first
- history cards are much easier to scan
- legacy pages now share a more consistent shell

The remaining gaps are narrower than the previous UX remediation review, but they are still worth fixing before calling the simplification pass fully done:

- one responsive regression in `CourierWork.vue`
- one remaining duplicate-feedback pattern in `RealtimeMap.vue`
- one page (`Settings.vue`) that still carries more always-open explanatory copy than the plan intended
