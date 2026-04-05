# Thesis-Safe Real-Road Routing Upgrade Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the current straight-line dispatch flow into a real-road routing flow while keeping `K-Means` clustering and `GA` route optimization as the thesis-defining core algorithms.

**Architecture:** Keep the existing two-stage pipeline intact: constrained `K-Means` still partitions packages into courier clusters, and `GeneticAlgorithmTSP` still optimizes visit order inside each cluster. Replace only the distance model and route geometry source: use a routing provider to build a road-network matrix for GA fitness evaluation and request final turn-by-turn geometry only after the stop order is fixed. This preserves the thesis scope while making distance, duration, and map output realistic.

**Tech Stack:** FastAPI, SQLAlchemy, NumPy, existing custom `K-Means` and `GA` modules, OpenRouteService Python client, Vue 3, TypeScript, Leaflet, Pytest, Vitest

---

## Thesis Guardrails

- The thesis title remains valid only if these rules hold during implementation:
  - `K-Means` remains the cluster assignment algorithm.
  - `GA` remains the stop-order optimization algorithm.
  - the routing provider does not choose clusters or final stop order.
  - the routing provider is used only for road-network distance/time estimation and final route geometry generation.
- Do not replace the dispatch core with OR-Tools, a hosted VRP solver, or provider-side optimization endpoints.
- Do not rewrite clustering into a non-`K-Means` method in this iteration.
- Treat any road-aware clustering enhancement as an optional later section, not part of the first deliverable.

## Current Baseline In This Repo

- `backend/app/core/algorithms/kmeans.py`
  - clustering distance uses `haversine_distance`
  - this is acceptable as the initial region split for the thesis
- `backend/app/core/algorithms/genetic.py`
  - fitness currently sums Haversine leg distances
  - this is the main place that must become road-aware
- `backend/app/services/dispatch_service.py`
  - computes route distance from straight segments
  - stores `geo_json.coordinates` as stop-to-stop straight lines
- `frontend/src/views/SmartDispatch.vue`
  - draws `geo_json.coordinates` as the visible polyline
  - assumes the same coordinates array is both the map path and the stop list
- `frontend/src/views/RealtimeMap.vue`
  - uses the same assumption for playback steps and package markers

## Recommended Delivery Strategy

Use a three-layer routing model:

1. `K-Means` still clusters packages with the current coordinate-based implementation.
2. For each cluster, request a road-network matrix for `[depot + cluster stops]` and pass that matrix into `GA` as the fitness cost source.
3. After `GA` returns the best package order, request one final directions geometry for the ordered stops and persist:
   - full road polyline for map rendering
   - ordered stop coordinates for markers and playback
   - total road distance
   - total road duration
   - per-leg summary if available

This is the lowest-risk version that meaningfully improves realism without breaking thesis positioning.

## Out Of Scope For The First Iteration

- replacing constrained `K-Means` with a road-network clustering algorithm
- real-time traffic prediction
- dynamic re-routing during delivery execution
- multi-depot support
- provider failover across multiple map vendors
- polyline animation along every road vertex during playback

## File Map

- Create: `backend/app/services/routing_service.py`
  - provider wrapper for matrix and directions requests
  - response normalization into repo-local structures
- Modify: `backend/app/core/config.py`
  - add routing provider configuration and strict/fallback mode
- Modify: `backend/app/services/dispatch_service.py`
  - inject routing service into cluster optimization flow
  - use matrix cost for GA
  - persist final road geometry and duration
- Modify: `backend/app/core/algorithms/genetic.py`
  - allow fitness evaluation from a precomputed matrix
- Modify: `backend/app/schemas/all_schemas.py`
  - keep schema compatible while documenting enriched `geo_json`
- Modify: `frontend/src/views/SmartDispatch.vue`
  - render full road polyline from path geometry
  - render markers from stop coordinates, not from the full path polyline
- Modify: `frontend/src/views/RealtimeMap.vue`
  - step courier playback by ordered stop list, not by every road vertex
- Modify: `frontend/src/lib/analytics.ts`
  - no metric change required if `total_distance_km` remains stable
  - optionally surface duration in later UI work
- Modify: `backend/tests/algorithms/test_algorithms.py`
  - add matrix-aware GA tests
- Modify: `backend/tests/test_config.py`
  - add routing config tests
- Create: `backend/tests/services/test_routing_service.py`
  - matrix normalization, directions normalization, fallback behavior
- Create: `backend/tests/services/__init__.py`
  - package initializer for service tests
- Modify: `backend/tests/test_dispatch_api.py`
  - verify plan output still serializes enriched route payloads
- Modify: `frontend/src/__tests__/SmartDispatch.spec.ts`
  - verify markers use `stop_coordinates`
  - verify polyline uses road-path coordinates
- Modify: `frontend/src/__tests__/RealtimeMap.spec.ts`
  - verify playback uses stop list instead of path vertex list

## Target Route Payload Shape

Keep `geo_json` backward-compatible at the top level, but add explicit separation between road path and delivery stops.

```json
{
  "type": "LineString",
  "coordinates": [[121.4737, 31.2304], [121.4741, 31.2306]],
  "stop_coordinates": [[121.4737, 31.2304], [121.4820, 31.2360], [121.4912, 31.2403], [121.4737, 31.2304]],
  "packages_ordered": [
    {
      "tracking_number": "TEST0001",
      "recipient_name": "张三",
      "weight": 1.2,
      "address": "上海市黄浦区南京东路 300 号"
    }
  ],
  "segments": [
    {
      "from_stop_index": 0,
      "to_stop_index": 1,
      "distance_km": 1.8,
      "duration_min": 6.5
    }
  ],
  "total_distance_km": 7.6,
  "estimated_duration_min": 28.4,
  "geometry_source": "openrouteservice",
  "optimization_metric": "road_distance",
  "status": "optimized"
}
```

Rules:

- `coordinates` means the full road polyline for display.
- `stop_coordinates` means ordered delivery stops including depot start and depot end.
- `packages_ordered[i]` maps to `stop_coordinates[i + 1]`.
- playback moves between stops, not across every polyline vertex.
- summary cards and analytics continue to read `total_distance_km`.

## Configuration Decision

Use strict routing mode by default for thesis runs.

```python
class Settings(BaseSettings):
    ROUTING_PROVIDER: str = "openrouteservice"
    ORS_API_KEY: str = ""
    ROUTING_PROFILE: str = "driving-car"
    ROUTING_STRICT_MODE: bool = True
    ROUTING_TIMEOUT_SECONDS: int = 20
```

Behavior:

- if `ROUTING_STRICT_MODE=True` and ORS config/request fails:
  - mark the plan as failed with a clear algorithm error
  - do not silently fall back to Haversine in thesis/demo runs
- if `ROUTING_STRICT_MODE=False`:
  - allow development fallback to Haversine for local debugging only

### Task 1: Add Routing Configuration And A Provider Abstraction

**Files:**
- Modify: `backend/app/core/config.py`
- Modify: `backend/tests/test_config.py`
- Create: `backend/app/services/routing_service.py`
- Create: `backend/tests/services/__init__.py`
- Create: `backend/tests/services/test_routing_service.py`

- [ ] **Step 1: Add failing config tests for routing settings**

Extend `backend/tests/test_config.py` with coverage for:

```python
from app.core.config import Settings

def test_settings_expose_routing_defaults(monkeypatch):
    monkeypatch.delenv("ORS_API_KEY", raising=False)
    settings = Settings()
    assert settings.ROUTING_PROVIDER == "openrouteservice"
    assert settings.ROUTING_PROFILE == "driving-car"
    assert settings.ROUTING_STRICT_MODE is True
```

- [ ] **Step 2: Run the config tests and confirm the new test fails**

Run:

```bash
cd backend && uv run pytest tests/test_config.py -v
```

Expected:

- one new failure because the routing fields are not defined yet

- [ ] **Step 3: Add routing settings in `backend/app/core/config.py`**

Add these fields to `Settings`:

```python
ROUTING_PROVIDER: str = "openrouteservice"
ORS_API_KEY: str = ""
ROUTING_PROFILE: str = "driving-car"
ROUTING_STRICT_MODE: bool = True
ROUTING_TIMEOUT_SECONDS: int = 20
```

- [ ] **Step 4: Create a normalized routing service wrapper**

Add `backend/app/services/routing_service.py` with a small interface:

```python
from dataclasses import dataclass

@dataclass
class RouteMatrix:
    distances_km: list[list[float]]
    durations_min: list[list[float]]

@dataclass
class RouteGeometry:
    coordinates: list[list[float]]
    total_distance_km: float
    estimated_duration_min: float
    segments: list[dict]

class RoutingService:
    def get_matrix(self, stops: list[tuple[float, float]]) -> RouteMatrix:
        raise NotImplementedError("matrix provider not implemented")

    def get_directions(self, ordered_stops: list[tuple[float, float]]) -> RouteGeometry:
        raise NotImplementedError("directions provider not implemented")
```

Normalization rules:

- input stop order is `(lat, lon)`
- stored/output geometry remains GeoJSON-style `[lon, lat]`
- matrix index `0` is always depot
- duration is stored in minutes, distance in kilometers

- [ ] **Step 5: Add failing routing service tests with mocked ORS responses**

Create `backend/tests/services/test_routing_service.py` covering:

```python
def test_get_matrix_normalizes_distance_and_duration_units():
    service = RoutingService()
    matrix = service._normalize_matrix_response(
        {
            "distances": [[0, 1200], [1200, 0]],
            "durations": [[0, 300], [300, 0]],
        }
    )
    assert matrix.distances_km == [[0.0, 1.2], [1.2, 0.0]]
    assert matrix.durations_min == [[0.0, 5.0], [5.0, 0.0]]

def test_get_directions_returns_geojson_like_coordinates_and_summary():
    service = RoutingService()
    geometry = service._normalize_directions_response(
        {
            "features": [{
                "geometry": {"coordinates": [[121.47, 31.23], [121.48, 31.24]]},
                "properties": {
                    "summary": {"distance": 1800, "duration": 420},
                    "segments": [{"distance": 1800, "duration": 420}],
                },
            }]
        }
    )
    assert geometry.coordinates == [[121.47, 31.23], [121.48, 31.24]]
    assert geometry.total_distance_km == 1.8
    assert geometry.estimated_duration_min == 7.0

def test_strict_mode_raises_when_provider_is_unavailable():
    service = RoutingService()
    service._client = None
    with pytest.raises(RuntimeError):
        service.get_matrix([(31.23, 121.47), (31.24, 121.48)])
```

Use `monkeypatch` to stub the ORS client methods instead of making network calls.

- [ ] **Step 6: Run the targeted backend tests and confirm failure before implementation**

Run:

```bash
cd backend && uv run pytest tests/test_config.py tests/services/test_routing_service.py -v
```

Expected:

- config tests pass only after settings are added
- service tests fail until `RoutingService` is implemented

### Task 2: Make `GeneticAlgorithmTSP` Matrix-Aware Without Replacing GA

**Files:**
- Modify: `backend/app/core/algorithms/genetic.py`
- Modify: `backend/tests/algorithms/test_algorithms.py`

- [ ] **Step 1: Add a failing GA regression test for precomputed road matrices**

Add a test like:

```python
def test_genetic_algorithm_supports_precomputed_cost_matrix():
    ga = GeneticAlgorithmTSP(population_size=20, generations=40)
    addresses = [(0.0, 0.0), (0.0, 0.0), (0.0, 0.0)]
    cost_matrix = [
        [0, 10, 3, 8],
        [10, 0, 2, 4],
        [3, 2, 0, 1],
        [8, 4, 1, 0],
    ]
    route, _ = ga.solve(addresses, (0.0, 0.0), cost_matrix=cost_matrix)
    assert sorted(route) == [0, 1, 2]
```

The test does not care about geometry coordinates; it cares that the solver accepts and uses a matrix while keeping the same external role.

- [ ] **Step 2: Run the algorithm tests and confirm the new test fails**

Run:

```bash
cd backend && uv run pytest tests/algorithms/test_algorithms.py -v
```

Expected:

- failure because the current `solve()` signature has no `cost_matrix` parameter

- [ ] **Step 3: Extend the GA interface to accept an optional cost matrix**

Update the solver signature:

```python
def solve(
    self,
    addresses: List[Tuple[float, float]],
    depot: Tuple[float, float],
    progress_callback=None,
    cost_matrix: Optional[List[List[float]]] = None,
) -> Tuple[List[int], List[float]]:
```

Implementation rules:

- keep existing Haversine behavior when `cost_matrix is None`
- if `cost_matrix` is provided:
  - index `0` is depot
  - address `i` maps to matrix index `i + 1`
  - `_fitness` must sum matrix costs, not coordinate distances
- keep `2-opt`, mutation, crossover, and elite retention unchanged

- [ ] **Step 4: Add a private helper that converts chromosome order into matrix indices**

Suggested helper:

```python
def _route_cost_from_matrix(self, chromosome: List[int], cost_matrix: List[List[float]]) -> float:
    order = [0] + [idx + 1 for idx in chromosome] + [0]
    return sum(cost_matrix[order[i]][order[i + 1]] for i in range(len(order) - 1))
```

- [ ] **Step 5: Re-run the algorithm tests and confirm they pass**

Run:

```bash
cd backend && uv run pytest tests/algorithms/test_algorithms.py -v
```

Expected:

- all existing algorithm tests still pass
- the new matrix-aware test passes

### Task 3: Integrate Road-Network Matrix Evaluation Into Dispatch Flow

**Files:**
- Modify: `backend/app/services/dispatch_service.py`
- Create: `backend/tests/services/test_dispatch_service.py`

- [ ] **Step 1: Add failing dispatch-service tests for matrix-backed optimization**

Create `backend/tests/services/test_dispatch_service.py` with a focused unit test that:

- seeds one station, several pending packages, and available couriers
- monkeypatches `RoutingService.get_matrix()` to return deterministic road costs
- monkeypatches `RoutingService.get_directions()` to return deterministic geometry
- runs `DispatchService.run_dispatch_algorithm(plan_id)`
- asserts that each `DeliveryRoute.geo_json` contains:
  - `coordinates`
  - `stop_coordinates`
  - `estimated_duration_min`
  - `geometry_source == "openrouteservice"`

Suggested assertion shape:

```python
assert route.geo_json["geometry_source"] == "openrouteservice"
assert len(route.geo_json["stop_coordinates"]) == route.geo_json["package_count"] + 2
assert route.total_distance > 0
assert route.estimated_time > 0
```

- [ ] **Step 2: Run the new dispatch service tests and confirm failure**

Run:

```bash
cd backend && uv run pytest tests/services/test_dispatch_service.py -v
```

Expected:

- failure because dispatch currently has no routing service integration and no duration persistence

- [ ] **Step 3: Inject `RoutingService` into `DispatchService`**

Refactor constructor:

```python
class DispatchService:
    def __init__(self, db: Session, routing_service: RoutingService | None = None):
        self.db = db
        self.routing_service = routing_service or RoutingService()
```

- [ ] **Step 4: Build a cluster-level road matrix before GA starts**

In the cluster loop, replace direct Haversine-only evaluation with:

```python
cluster_stops = [depot_coord] + cluster_coords
matrix = self.routing_service.get_matrix(cluster_stops)
best_route_indices, _ = ga.solve(
    cluster_coords,
    depot_coord,
    progress_callback=ga_progress_callback,
    cost_matrix=matrix.distances_km,
)
```

Use `distances_km` as the optimization metric for the first iteration. Keep `durations_min` available in case the thesis write-up later wants a time-based experiment.

- [ ] **Step 5: Keep optimization-progress rendering cheap**

Update the progress callback so it does not request full directions geometry every few generations.

Rules:

- progress view may keep using ordered stop coordinates as a preview
- progress distance should be computed from the precomputed matrix, not repeated provider calls
- final road polyline should be requested only once after the best order is fixed

Suggested helper:

```python
def summarize_order_from_matrix(best_route_indices, matrix):
    order = [0] + [idx + 1 for idx in best_route_indices] + [0]
    total_distance = sum(matrix.distances_km[order[i]][order[i + 1]] for i in range(len(order) - 1))
    total_duration = sum(matrix.durations_min[order[i]][order[i + 1]] for i in range(len(order) - 1))
    return total_distance, total_duration
```

- [ ] **Step 6: Replace final straight-line route persistence with final road geometry persistence**

After GA returns the best order:

```python
ordered_stop_coords = [depot_coord] + [(p.latitude, p.longitude) for p in ordered_packages] + [depot_coord]
route_geometry = self.routing_service.get_directions(ordered_stop_coords)
```

Persist:

```python
route.geo_json = {
    "type": "LineString",
    "coordinates": route_geometry.coordinates,
    "stop_coordinates": [[lon, lat] for lat, lon in ordered_stop_coords],
    "segments": route_geometry.segments,
    "total_distance_km": round(route_geometry.total_distance_km, 2),
    "estimated_duration_min": round(route_geometry.estimated_duration_min, 2),
    "geometry_source": "openrouteservice",
    "optimization_metric": "road_distance",
    "package_count": len(ordered_packages),
    "total_weight": round(sum(getattr(p, "weight", 1.0) or 1.0 for p in ordered_packages), 1),
    "color": ROUTE_COLORS[cluster_idx % len(ROUTE_COLORS)],
    "status": "optimized",
    "packages_ordered": [
        {
            "tracking_number": p.tracking_number,
            "recipient_name": p.recipient_name,
            "weight": getattr(p, "weight", 1.0),
            "address": p.recipient_address,
        } for p in ordered_packages
    ],
}
route.total_distance = route_geometry.total_distance_km
route.estimated_time = route_geometry.estimated_duration_min
```

- [ ] **Step 7: Re-run the dispatch service tests and then the broader dispatch API tests**

Run:

```bash
cd backend && uv run pytest tests/services/test_dispatch_service.py tests/test_dispatch_api.py -v
```

Expected:

- service tests pass
- API tests still pass after route payload enrichment

### Task 4: Keep API And Schema Contracts Stable While Enriching Route Data

**Files:**
- Modify: `backend/app/schemas/all_schemas.py`
- Modify: `backend/tests/test_dispatch_api.py`

- [ ] **Step 1: Add a failing API assertion for route duration and stop coordinates**

Extend an API-level test so a route payload is expected to contain:

```python
assert "stop_coordinates" in route["geo_json"]
assert "estimated_duration_min" in route["geo_json"]
```

Use a monkeypatched dispatch run or seeded route fixture if needed.

- [ ] **Step 2: Run the API tests and confirm failure**

Run:

```bash
cd backend && uv run pytest tests/test_dispatch_api.py -v
```

Expected:

- failure until enriched route payload is serialized

- [ ] **Step 3: Preserve backward compatibility in schema usage**

No breaking schema redesign is necessary because `geo_json` is already `dict`, but update comments and route field documentation so future code assumes:

```python
class RouteBase(BaseModel):
    total_distance: float = 0.0
    estimated_time: float = 0.0
    geo_json: Optional[dict] = None
```

Implementation rule:

- continue exposing `total_distance`
- persist `estimated_time` in minutes
- keep `geo_json.total_distance_km` for frontend and analytics compatibility

- [ ] **Step 4: Re-run API tests and confirm pass**

Run:

```bash
cd backend && uv run pytest tests/test_dispatch_api.py -v
```

Expected:

- dispatch API contract remains stable
- enriched route payload is available to the frontend

### Task 5: Separate Road Polyline Rendering From Stop Rendering In The Frontend

**Files:**
- Modify: `frontend/src/views/SmartDispatch.vue`
- Modify: `frontend/src/views/RealtimeMap.vue`
- Modify: `frontend/src/__tests__/SmartDispatch.spec.ts`
- Modify: `frontend/src/__tests__/RealtimeMap.spec.ts`

- [ ] **Step 1: Add failing frontend regression tests for the new route shape**

Add tests asserting:

- `SmartDispatch.vue`
  - polyline reads `route.geo_json.coordinates`
  - package markers read `route.geo_json.stop_coordinates.slice(1, -1)`
- `RealtimeMap.vue`
  - playback steps read `stop_coordinates`
  - package marker count is derived from `stop_coordinates`, not from full path vertices

Suggested mock payload:

```ts
geo_json: {
  coordinates: [[121.47, 31.23], [121.471, 31.231], [121.472, 31.232], [121.473, 31.233]],
  stop_coordinates: [[121.47, 31.23], [121.472, 31.232], [121.473, 31.233], [121.47, 31.23]],
  packages_ordered: [
    { recipient_name: 'A', tracking_number: 'T1', weight: 1, address: 'Addr A' },
    { recipient_name: 'B', tracking_number: 'T2', weight: 2, address: 'Addr B' }
  ],
  total_distance_km: 6.2,
  estimated_duration_min: 19.5
}
```

- [ ] **Step 2: Run the targeted frontend tests and confirm failure**

Run:

```bash
cd frontend && npm run test:unit -- SmartDispatch RealtimeMap
```

Expected:

- at least one test fails because current components assume one coordinates array serves both path and stops

- [ ] **Step 3: Update `SmartDispatch.vue` to use separate data sources**

Implementation rules:

- keep polyline source:

```ts
const pathCoords = route.geo_json.coordinates || []
const latlngs = pathCoords.map((coord: any) => [coord[1], coord[0]])
```

- change marker source:

```ts
const stopCoords = route.geo_json.stop_coordinates || route.geo_json.coordinates || []
stopCoords.slice(1, -1).forEach((coord: any, packageIndex: number) => {
  const marker = L.marker([coord[1], coord[0]], { icon }).addTo(routeLayerGroup.value)
  marker.bindPopup(orderedPackages[packageIndex]?.recipient_name || '收件人')
})
```

- continue summing:

```ts
totalDistance += route.geo_json.total_distance_km || 0
```

- [ ] **Step 4: Update `RealtimeMap.vue` to step by ordered stops**

Implementation rules:

- route outline uses full `coordinates`
- package markers use `stop_coordinates`
- playback position changes use:

```ts
const coords = courier.route.geo_json?.stop_coordinates
const nextCoord = coords[courier.delivered + 1]
```

This preserves readable playback. Do not move the truck marker through every road vertex in the first iteration.

- [ ] **Step 5: Re-run frontend tests and confirm pass**

Run:

```bash
cd frontend && npm run test:unit -- SmartDispatch RealtimeMap
```

Expected:

- route rendering passes with the enriched backend payload
- playback semantics remain stop-based and deterministic

### Task 6: Add Integration Verification For Thesis-Safe Real-Road Dispatch

**Files:**
- Modify: `README_zh-CN.md`
- Modify: `README.md`
- Modify: `docs/快递末端配送系统设计文档.md`

- [ ] **Step 1: Update project docs so the algorithm description stays thesis-accurate**

Adjust wording in the Chinese design document and README files:

- from:
  - route distance is based on straight-line/Haversine approximation
- to:
  - clustering still uses constrained `K-Means`
  - intra-cluster sequencing still uses custom `GA`
  - route evaluation now uses road-network distance matrix
  - final map geometry is generated from real road paths

Suggested wording for the thesis-alignment paragraph:

```md
系统总体仍采用“K-Means 聚类 + 遗传算法”的两阶段优化框架。
其中，K-Means 负责多车任务分区，遗传算法负责每个分区内的访问顺序优化；
真实道路网络数据仅用于距离/时长度量修正与最终路径几何生成，
因此系统核心求解逻辑未偏离论文题目。
```

- [ ] **Step 2: Run backend and frontend test suites relevant to the routing upgrade**

Run:

```bash
cd backend && uv run pytest tests/test_config.py tests/algorithms/test_algorithms.py tests/services/test_routing_service.py tests/services/test_dispatch_service.py tests/test_dispatch_api.py -v
```

Run:

```bash
cd frontend && npm run test:unit -- SmartDispatch RealtimeMap analytics-summary RouteHistory
```

Expected:

- all targeted tests pass
- metrics pages still read `total_distance_km` unchanged

- [ ] **Step 3: Perform one manual end-to-end dispatch verification with a real ORS key**

Manual checks:

1. Set `ORS_API_KEY` in `backend/.env`.
2. Reset demo data.
3. Start one dispatch.
4. Verify the generated route line follows roads instead of straight stop-to-stop chords.
5. Verify route cards show non-zero `total_distance_km`.
6. Verify `estimated_duration_min` is non-zero in the stored route JSON.
7. Verify playback still advances one delivery stop per click.
8. Verify if ORS is unreachable and `ROUTING_STRICT_MODE=True`, the plan fails explicitly instead of silently producing fake results.

- [ ] **Step 4: Commit**

```bash
git add backend/app/core/config.py \
  backend/app/core/algorithms/genetic.py \
  backend/app/services/dispatch_service.py \
  backend/app/services/routing_service.py \
  backend/app/schemas/all_schemas.py \
  backend/tests/test_config.py \
  backend/tests/test_dispatch_api.py \
  backend/tests/algorithms/test_algorithms.py \
  backend/tests/services/__init__.py \
  backend/tests/services/test_routing_service.py \
  backend/tests/services/test_dispatch_service.py \
  frontend/src/views/SmartDispatch.vue \
  frontend/src/views/RealtimeMap.vue \
  frontend/src/__tests__/SmartDispatch.spec.ts \
  frontend/src/__tests__/RealtimeMap.spec.ts \
  README.md \
  README_zh-CN.md \
  docs/快递末端配送系统设计文档.md
git commit -m "feat: add thesis-safe real-road routing pipeline"
```

## Optional Phase 2 After The First Deliverable

Only start this after Phase 1 is stable and documented.

- experiment with `durations_min` as the GA objective instead of `distances_km`
- add a thesis comparison section:
  - Haversine objective vs road-distance objective
  - route length gap
  - duration gap
  - runtime increase
- evaluate whether constrained `K-Means` should receive a light road-aware correction term for depot distance, while still remaining clearly `K-Means`

## Risks And Controls

- ORS latency or quota pressure
  - control: matrix once per cluster, directions once per final route, no per-generation geometry calls
- frontend regressions because path and stops were previously conflated
  - control: explicit `stop_coordinates` contract and targeted UI regression tests
- thesis drift
  - control: keep provider limited to matrix + geometry, not optimization
- silent fake-success behavior when the map provider fails
  - control: strict mode by default for academic/demo runs

## Definition Of Done

- dispatch still runs as `K-Means -> GA -> route persistence`
- `GA` evaluates candidate routes with a road-network matrix
- final stored route geometry follows real roads
- route payload separates full path geometry from delivery stops
- Smart Dispatch and Realtime Map both render correctly against the new payload
- backend tests and targeted frontend tests pass
- project docs explicitly explain why the thesis title still matches the implementation
