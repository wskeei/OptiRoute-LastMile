# Single Main Station And Demo Randomization Review

Date: 2026-04-05
Plan: `docs/superpowers/plans/2026-04-05-single-main-station-and-demo-randomization-plan.md`
Reviewed branch/worktree: `feat/single-main-station-demo-randomization` in `.worktrees/single-main-station-demo-randomization`
Base SHA: `3ababce8747fb198392a912f6fb061151d78d8b6`
Head SHA: `57878f8b5c42f5c43090ee7420af5b6db58fbd79`

## Scope

This review checks whether the implementation in `.worktrees/single-main-station-demo-randomization` satisfies the approved plan, with emphasis on:

- single-main-station backend semantics
- station-aware demo data generation
- frontend dynamic station usage
- reset behavior and historical data correctness
- targeted test coverage versus the planned behavior

## Findings

### P1: `reset-demo` does not actually regenerate packages or couriers from scratch, so it can return a “successful” reset with zero usable sample data

Plan mismatch:

- The plan explicitly requires `randomize_station=false` and `randomize_station=true` to regenerate packages and couriers around the selected station.
- The current implementation only reuses existing `Package` and `Courier` rows. If the database is empty or sparse, it returns success with no usable sample set.

Evidence:

- `docs/superpowers/plans/2026-04-05-single-main-station-and-demo-randomization-plan.md:85`
- `docs/superpowers/plans/2026-04-05-single-main-station-and-demo-randomization-plan.md:88`
- `.worktrees/single-main-station-demo-randomization/backend/app/api/v1/endpoints/dispatch.py:135`
- `.worktrees/single-main-station-demo-randomization/backend/app/api/v1/endpoints/dispatch.py:138`
- `.worktrees/single-main-station-demo-randomization/backend/app/api/v1/endpoints/dispatch.py:170`
- `.worktrees/single-main-station-demo-randomization/backend/app/api/v1/endpoints/dispatch.py:174`
- `.worktrees/single-main-station-demo-randomization/backend/tests/test_dispatch_api.py:124`

Why this matters:

- In a fresh or partially cleaned database, `reset-demo` can return:
  - `pending_packages = 0`
  - `available_couriers = 0`
  - `message = "Demo data reset successfully"`
- That directly contradicts the page-level promise that reset actions prepare demo data for dispatch.
- The current API tests do not catch this because they always seed 10 packages and 3 couriers before calling the endpoint.

Verification:

- Ad-hoc reproduction on a database containing only one station and no packages/couriers returned:
  - `pending_packages: 0`
  - `available_couriers: 0`
  - success response instead of generating fresh sample rows

Suggested fix:

- Make `reset-demo` generate missing package and courier rows when the current counts are insufficient, instead of only reclassifying existing rows.
- At minimum, guarantee a non-zero target sample set for both packages and couriers.
- Add an API test that starts from a station-only database and asserts the endpoint creates usable demo data.

### P1: Editing or randomizing the main station mutates historical plan station context in place

Plan mismatch:

- The plan introduces one editable main station, but the current implementation updates the existing `DeliveryStation` row in place.
- `DeliveryPlan.station_id` is a foreign key to that same row, so historical plans silently change city/name/coordinates after every main-station edit or random-city reset.

Evidence:

- `.worktrees/single-main-station-demo-randomization/backend/app/models/all_models.py:94`
- `.worktrees/single-main-station-demo-randomization/backend/app/models/all_models.py:101`
- `.worktrees/single-main-station-demo-randomization/backend/app/services/station_service.py:41`
- `.worktrees/single-main-station-demo-randomization/backend/app/services/station_service.py:42`
- `.worktrees/single-main-station-demo-randomization/backend/app/services/station_service.py:45`
- `.worktrees/single-main-station-demo-randomization/backend/app/api/v1/endpoints/dispatch.py:116`

Why this matters:

- A completed plan created in Shanghai can become associated with “成都春熙路配送站” after a later random-city reset, even though its routes and package geometry still belong to the old city.
- This corrupts historical meaning and makes plan metadata inconsistent with persisted route geometry.
- The bug is especially visible because the feature adds station randomization without clearing history by default.

Verification:

- Ad-hoc reproduction:
  - create a station and one completed plan pointing to it
  - call `StationService.update_main_station(...)`
  - reload the plan
  - the plan’s related station now reflects the new city, not the original one

Suggested fix:

- Preserve historical station context instead of mutating the station row that old plans reference.
- Two viable options:
  - create a new station row when the main station changes, and make future flows use the new row
  - snapshot station name/address/coordinates into `DeliveryPlan.algorithm_meta` or dedicated plan fields when the plan is created
- Add a regression test asserting that an existing plan’s station context remains stable after a main-station update.

### P1: Current-station coordinates are incorrectly used as the depot for replaying the latest completed route

Plan mismatch:

- The plan requires `SmartDispatch` and `RealtimeMap` to load the current station dynamically, but it does not authorize overriding the actual depot of a previously completed route.
- The implementation uses current-station coordinates for map center, station marker, courier reset position, and initial courier position even when replaying an older plan.

Evidence:

- `.worktrees/single-main-station-demo-randomization/frontend/src/views/SmartDispatch.vue:183`
- `.worktrees/single-main-station-demo-randomization/frontend/src/views/SmartDispatch.vue:224`
- `.worktrees/single-main-station-demo-randomization/frontend/src/views/SmartDispatch.vue:245`
- `.worktrees/single-main-station-demo-randomization/frontend/src/views/RealtimeMap.vue:60`
- `.worktrees/single-main-station-demo-randomization/frontend/src/views/RealtimeMap.vue:81`
- `.worktrees/single-main-station-demo-randomization/frontend/src/views/RealtimeMap.vue:224`
- `.worktrees/single-main-station-demo-randomization/frontend/src/views/RealtimeMap.vue:268`
- `.worktrees/single-main-station-demo-randomization/frontend/src/__tests__/RealtimeMap.spec.ts:143`

Why this matters:

- If the user changes the main station after the last completed plan was generated, the monitor page will:
  - center the map on the new station
  - place the depot marker at the new station
  - start courier playback from the new station
  - while still replaying route geometry from the older plan
- This makes the latest-route replay geographically inconsistent and can place the route off-screen or make the courier “jump” from the wrong city.
- `SmartDispatch` has the same risk when restoring the latest plan after the main station changes but before a new dispatch is run.

Suggested fix:

- Separate “current main station” from “route depot for an existing plan”.
- When replaying or restoring a completed route:
  - derive the depot from the route data itself, ideally `route.geo_json.coordinates[0]` or a dedicated persisted depot field
  - only use the current main station for current-sample markers and future dispatch actions
- Add a regression test where the current main station differs from the latest completed route depot and assert replay starts from the route depot, not the current station.

### P2: Settings hardcodes `totalStations = 1` while claiming the stats come from “actual API sample counts”

Plan mismatch:

- The plan keeps single-main-station UI semantics, but the backend still allows multiple station rows and explicitly defines deterministic behavior when multiple rows exist.
- The Settings page currently claims “来自接口的实际样本数量”, yet `totalStations` is set to `1` unconditionally instead of reading actual data.

Evidence:

- `docs/superpowers/plans/2026-04-05-single-main-station-and-demo-randomization-plan.md:117`
- `.worktrees/single-main-station-demo-randomization/frontend/src/views/Settings.vue:118`
- `.worktrees/single-main-station-demo-randomization/frontend/src/views/Settings.vue:131`
- `.worktrees/single-main-station-demo-randomization/frontend/src/views/Settings.vue:141`

Why this matters:

- The UI text says the numbers come from the API, but one of them is fabricated.
- If extra station rows exist, the stats panel becomes misleading exactly in the scenario the backend contract is designed to handle.

Suggested fix:

- Either:
  - fetch `/api/v1/delivery/stations` and display the real count
  - or relabel the stat to make it explicit that the page is showing “当前主站点数” rather than raw table count

## Verification Performed

- `cd .worktrees/single-main-station-demo-randomization/backend && uv run pytest tests/services/test_station_service.py tests/services/test_demo_data_service.py tests/test_dispatch_api.py -q`
  - Result: passed, 12 tests passed.
- `cd .worktrees/single-main-station-demo-randomization/frontend && npm run test:unit -- LegacyPages SmartDispatch RealtimeMap`
  - Result: passed, 3 test files and 17 tests passed.
- Ad-hoc reproductions:
  - `reset-demo` on a station-only database returned a success response with zero packages and zero couriers
  - updating the main station changed the related station data of an already-created historical plan

## Overall Assessment

The branch does implement the core direction of the plan:

- one editable current station endpoint exists
- Settings can edit the main station
- Smart Dispatch and Realtime Map load the current station dynamically
- demo data generation is station-aware
- random-city station seeds are present
- the dispatch algorithm remains on the original straight-line/Haversine model

However, the implementation does not fully satisfy the plan yet. The main remaining gaps are:

- `reset-demo` does not guarantee usable sample regeneration
- historical plan station context is rewritten by later main-station updates
- current-station coordinates override historical route depot semantics in replay/restore flows
- Settings stats are not fully truthful about station counts
