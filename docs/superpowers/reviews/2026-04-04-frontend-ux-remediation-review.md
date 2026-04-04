# Frontend UX Remediation Review

Date: 2026-04-04
Plan: `docs/superpowers/plans/2026-04-04-frontend-ux-remediation-plan.md`
Reviewed branch/worktree: `feature/frontend-ux-remediation` in `.worktrees/frontend-ux-remediation`
Base SHA: `be68cf8`
Head SHA: `d268d2a`

## Scope

This review checks whether the implementation in `.worktrees/frontend-ux-remediation` satisfies the remediation plan, with emphasis on:

- trust and capability truthfulness
- first-run task flow
- information architecture and navigation priority
- responsive behavior and persistent feedback
- visual normalization only after the above

## Findings

### P1: Route history still lacks a recoverable empty state

Plan mismatch:

- Phase 2 requires empty and no-history states to point to a concrete next action.
- Current implementation only renders the normal history layout. When there are no completed plans, the page falls through to an empty chart container and an empty list.

Evidence:

- `frontend/src/views/RouteHistory.vue:18`
- `frontend/src/views/RouteHistory.vue:25`
- `frontend/src/views/RouteHistory.vue:152`

Why this matters:

- A first-run user can still land on the history page and get no meaningful guidance.
- This misses the plan requirement that the first successful dispatch path should be teachable without external explanation.

Suggested fix:

- Add an explicit `plans.length === 0` empty state before the grid/compare UI.
- The empty state should explain that no completed dispatch exists yet and link back to `/dispatch`.
- Reuse the same task language already established in `ONBOARDING_STEPS`.

### P1: Information architecture and mobile navigation are improved, but not fully remediated

Plan mismatch:

- Phase 3 requires reducing navigation noise and foregrounding core operations.
- Phase 4 requires core pages to work at 375px without horizontal scrolling.
- The current app still exposes eight top-level destinations, and on mobile the sidebar becomes a horizontally scrollable nav strip.

Evidence:

- `frontend/src/lib/ux.ts:23`
- `frontend/src/App.vue:31`
- `frontend/src/App.vue:271`
- `frontend/src/App.vue:277`
- `frontend/src/views/RouteHistory.vue:96`

Why this matters:

- Horizontal scrolling in primary navigation is still a weak mobile interaction for a task-oriented product.
- Keeping all eight destinations at the same level weakens the “dispatch first, analysis second” hierarchy the plan called for.
- History detail drawer width is still fixed at `460px`, which is risky on narrow screens.

Suggested fix:

- Reduce or regroup top-level navigation on small screens so core actions stay immediately visible without sideways scrolling.
- Make the history detail drawer responsive instead of fixed-width.
- Consider demoting lower-priority destinations behind a “more” pattern or secondary grouping if the product must keep all pages.

### P1: “Latest plan” selection is inconsistent and can surface stale data

Plan mismatch:

- Phase 1 requires core metrics and states to remain defensible and truthful.
- Several pages treat the first returned plan as the latest plan without sorting, while `RealtimeMap.vue` explicitly sorts by descending ID.

Evidence:

- `frontend/src/views/SmartDispatch.vue:223`
- `frontend/src/lib/analytics.ts:15`
- `frontend/src/views/Analytics.vue:182`
- `frontend/src/views/Dashboard.vue:155`
- `frontend/src/views/RealtimeMap.vue:91`

Why this matters:

- If `/api/v1/dispatch/plans` is not guaranteed to return newest-first, the UI may label older plans as “latest” or “recent”.
- That would directly undercut the trust work done elsewhere in this remediation.

Suggested fix:

- Centralize plan ordering in one helper and use it everywhere.
- Sort completed plans explicitly by `created_at` or `id` descending before deriving “latest”, “recent 8”, “recent 10”, or ranking summaries.
- Do not rely on backend response order unless that contract is documented and tested.

### P2: Persistent feedback is still incomplete on several read-heavy pages

Plan mismatch:

- Phase 4 requires error, loading, and empty states to remain visible long enough to guide recovery.
- Dashboard and analytics still fail silently from a user perspective: they `console.error(...)` and leave users with empty charts or default zero values.
- Smart dispatch still relies heavily on transient toast messaging for important failures during polling.

Evidence:

- `frontend/src/views/Dashboard.vue:127`
- `frontend/src/views/Dashboard.vue:207`
- `frontend/src/views/Analytics.vue:167`
- `frontend/src/views/Analytics.vue:197`
- `frontend/src/views/SmartDispatch.vue:251`
- `frontend/src/views/SmartDispatch.vue:268`

Why this matters:

- A user cannot reliably distinguish “there is no data yet” from “the page failed to load”.
- This is a product-grade usability gap, not just a polish issue.

Suggested fix:

- Add page-level loading, error, and empty state blocks on dashboard and analytics.
- Preserve failure context in the page body instead of only using `ElMessage`.
- On dispatch polling failure, show an inline status panel with recovery guidance and a retry action.

## Assumptions

- The stale-data finding assumes `/api/v1/dispatch/plans` does not formally guarantee newest-first ordering.
- If backend ordering is guaranteed and documented, that finding can be downgraded, but the frontend should still stay consistent across pages.

## Verification Performed

- `cd .worktrees/frontend-ux-remediation/frontend && npm run test:unit`
  - Result: passed, 3 test files and 9 tests passed.
- `cd .worktrees/frontend-ux-remediation/frontend && npm run build`
  - Result: passed.
- Note: `npm test` is not defined in `frontend/package.json`; the valid test script is `npm run test:unit`.

## Overall Assessment

The branch has addressed a substantial part of the plan:

- default routing and auth redirect now prioritize `/dispatch`
- major misleading control surfaces were reduced
- auth forms now use visible labels
- several pages now explain demo-vs-real behavior more clearly

However, the implementation does not fully meet the plan’s definition of done yet. The remaining gaps are concentrated in:

- no-history recovery guidance
- mobile IA and navigation behavior
- consistent “latest plan” derivation
- persistent page-level feedback states
