# Thesis-Safe Real-Road Routing Upgrade Review

Date: 2026-04-05
Plan: `docs/superpowers/plans/2026-04-05-thesis-safe-real-road-routing-upgrade.md`
Reviewed branch/worktree: `optimization/thesis-safe-real-road-routing-upgrade` in `.worktrees/thesis-safe-real-road-routing-upgrade`
Base SHA: `372ee44dfee689f78dd5ec606534fbfaa2f6d7a9`
Head SHA: `7d60653e6c46a14bdb2ac16f2981fc50290c08fe`

## Scope

This review checks whether the implementation in `.worktrees/thesis-safe-real-road-routing-upgrade` satisfies the approved plan, with emphasis on:

- thesis guardrails around `K-Means` + `GA`
- routing-provider integration behavior
- route payload contract
- frontend rendering/playback behavior
- test coverage versus the required behavior

## Findings

### P1: `ROUTING_STRICT_MODE=False` does not implement the planned Haversine fallback and can either crash the dispatch or produce a fake success

Plan mismatch:

- The plan requires non-strict mode to "allow development fallback to Haversine for local debugging only".
- The current implementation does not build a Haversine matrix or geometry fallback anywhere.

Evidence:

- `docs/superpowers/plans/2026-04-05-thesis-safe-real-road-routing-upgrade.md:163`
- `.worktrees/thesis-safe-real-road-routing-upgrade/backend/app/services/routing_service.py:81`
- `.worktrees/thesis-safe-real-road-routing-upgrade/backend/app/services/routing_service.py:84`
- `.worktrees/thesis-safe-real-road-routing-upgrade/backend/app/services/routing_service.py:86`
- `.worktrees/thesis-safe-real-road-routing-upgrade/backend/app/services/routing_service.py:100`
- `.worktrees/thesis-safe-real-road-routing-upgrade/backend/app/services/dispatch_service.py:158`
- `.worktrees/thesis-safe-real-road-routing-upgrade/backend/app/services/dispatch_service.py:196`
- `.worktrees/thesis-safe-real-road-routing-upgrade/backend/tests/services/test_routing_service.py:102`

Why this matters:

- When matrix fallback returns `[]`, dispatch still passes `matrix.distances_km` into `GA`, which then indexes into an empty matrix and fails.
- When directions fallback returns an empty geometry, dispatch can still mark the plan `READY` and persist `0.0` distance, `0.0` duration, and `[]` coordinates while claiming `optimization_metric: "road_distance"`.
- That is worse than a clean failure because it creates apparently successful but invalid route data.

Verification:

- Ad-hoc reproduction with a non-strict routing stub returning an empty matrix caused:
  - `Algorithm Error: list index out of range`
  - plan status reset to `DRAFT`
- Ad-hoc reproduction with a valid matrix but empty directions caused:
  - plan status `READY`
  - route distance `0.0`
  - route duration `0.0`
  - empty persisted coordinates

Suggested fix:

- Implement an actual non-strict fallback path:
  - build a Haversine matrix when ORS matrix retrieval fails
  - derive stop-to-stop fallback geometry from ordered stops when directions retrieval fails
- If that fallback is not desired anymore, remove the non-strict option and fail explicitly instead of returning empty structures.
- Replace the current service test that locks in `[]` matrix fallback with a dispatch-level test that verifies the intended fallback semantics.

### P1: Realtime playback regresses for existing routes that do not have `stop_coordinates`

Plan mismatch:

- The plan required the enriched payload to remain backward-compatible while separating full path geometry from stop coordinates.
- `RealtimeMap.vue` only partially applies the compatibility fallback: package markers fall back to `coordinates`, but playback does not.

Evidence:

- `docs/superpowers/plans/2026-04-05-thesis-safe-real-road-routing-upgrade.md:106`
- `.worktrees/thesis-safe-real-road-routing-upgrade/frontend/src/views/RealtimeMap.vue:122`
- `.worktrees/thesis-safe-real-road-routing-upgrade/frontend/src/views/RealtimeMap.vue:236`

Why this matters:

- Any completed route created before this branch, or any route imported without `stop_coordinates`, will still render a path and package markers.
- But `nextStep()` only reads `route.geo_json?.stop_coordinates`; if that field is absent, the courier marker never advances and the page silently degrades into warning logs plus incorrect "已送达" progress.
- This is a user-visible regression on a core page for existing data.

Suggested fix:

- In `nextStep()`, fall back to `coordinates` when `stop_coordinates` is missing.
- If you want to avoid using road-polyline vertices for playback, backfill `stop_coordinates` for legacy rows during migration or route-load normalization before simulation starts.
- Add a regression test covering an old completed route that has `coordinates` but no `stop_coordinates`.

### P2: The persisted `segments` payload does not match the plan’s normalized contract

Plan mismatch:

- The plan defines `segments` as a normalized per-leg summary with:
  - `from_stop_index`
  - `to_stop_index`
  - `distance_km`
  - `duration_min`
- The implementation stores raw ORS `segments` objects unchanged.

Evidence:

- `docs/superpowers/plans/2026-04-05-thesis-safe-real-road-routing-upgrade.md:121`
- `.worktrees/thesis-safe-real-road-routing-upgrade/backend/app/services/routing_service.py:59`
- `.worktrees/thesis-safe-real-road-routing-upgrade/backend/app/services/routing_service.py:70`
- `.worktrees/thesis-safe-real-road-routing-upgrade/backend/app/services/dispatch_service.py:218`
- `.worktrees/thesis-safe-real-road-routing-upgrade/backend/tests/services/test_routing_service.py:35`

Why this matters:

- The current payload is not the contract the plan approved.
- Consumers cannot reliably use `segments` for future UI, analytics, or thesis comparison work because they get provider-specific meter/second structures instead of normalized repo-local data.
- The existing tests now encode the raw provider shape, making future correction harder.

Suggested fix:

- Normalize `segments` inside `RoutingService._normalize_directions_response()`.
- Persist a repo-local structure with kilometer/minute units and stop-index metadata.
- Update the routing service tests to assert the normalized contract rather than the raw ORS response.

### P2: Provider failure is still recorded as `DRAFT`, not as an explicit failed optimization state

Plan mismatch:

- The plan explicitly says routing-provider failures in strict mode should "mark the plan as failed with a clear algorithm error".
- The implementation resets the plan to `DRAFT`.

Evidence:

- `docs/superpowers/plans/2026-04-05-thesis-safe-real-road-routing-upgrade.md:160`
- `.worktrees/thesis-safe-real-road-routing-upgrade/backend/app/services/dispatch_service.py:244`
- `.worktrees/thesis-safe-real-road-routing-upgrade/backend/app/services/dispatch_service.py:247`

Why this matters:

- `DRAFT` is indistinguishable from "not really started yet" rather than "optimization failed because routing was unavailable".
- This weakens auditability and makes route-provider outages harder to diagnose from the API or admin UI.
- It also diverges from the plan’s explicit failure semantics.

Suggested fix:

- Add a dedicated failed status, or at minimum persist a machine-readable failure state in `status`/`algorithm_meta` that the frontend and API can distinguish from a normal draft.
- Add an API-level test covering provider failure in strict mode and asserting the visible failure state.

## Verification Performed

- `cd .worktrees/thesis-safe-real-road-routing-upgrade/backend && uv run pytest tests/test_config.py tests/algorithms/test_algorithms.py tests/services/test_routing_service.py tests/services/test_dispatch_service.py tests/test_dispatch_api.py -q`
  - Result: passed, 26 tests passed.
- `cd .worktrees/thesis-safe-real-road-routing-upgrade/frontend && npm run test:unit -- SmartDispatch RealtimeMap analytics-summary RouteHistory`
  - Result: passed, 4 test files and 17 tests passed.
- Ad-hoc dispatch reproductions were run to verify non-strict fallback behavior:
  - empty matrix fallback path currently crashes dispatch
  - empty directions fallback path currently persists a `READY` plan with zeroed route metrics

## Overall Assessment

The branch does satisfy the main thesis guardrail:

- `K-Means` is still the clustering algorithm
- `GA` is still the route-order optimizer
- ORS is being used as a matrix/geometry provider rather than as the optimizer itself

However, the implementation does not fully satisfy the plan yet. The main remaining gaps are:

- non-strict fallback behavior is not implemented as specified and can create either hard failures or fake successes
- realtime playback regresses on legacy routes without `stop_coordinates`
- the `segments` payload contract is not normalized to the reviewed shape
- provider failures are not surfaced as an explicit failed optimization state
