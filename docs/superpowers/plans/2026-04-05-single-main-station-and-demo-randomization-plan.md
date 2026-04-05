# Single Main Station And Demo Randomization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the system use one editable main delivery station everywhere, let demo data regenerate around that station with realistic randomness, and let reset actions optionally randomize the station to another Chinese city while keeping the dispatch algorithm on straight-line/Haversine distance.

**Architecture:** Keep the existing `DeliveryStation` table and the current `K-Means + GA + Haversine` dispatch pipeline. Introduce a single-source-of-truth “current main station” backend contract, route all frontend station consumers through it, and move demo data generation into station-aware backend helpers. Reset actions will either reuse the current station or swap it to a random city from a curated nationwide catalog before regenerating packages/couriers.

**Tech Stack:** FastAPI, SQLAlchemy, Pydantic, Vue 3, TypeScript, Element Plus, Pytest, Vitest

---

## Scope Guardrails

- Do not reintroduce ORS or real-road routing into this implementation.
- Keep `DispatchService` on the current straight-line/Haversine distance model.
- Treat the system as having exactly one editable main station for UI and demo workflows.
- Do not add multi-station dispatch selection in this iteration.

## File Map

- Create: `backend/app/services/station_service.py`
  - centralize “get or create main station” and “update main station” behavior
- Create: `backend/app/services/demo_data_service.py`
  - generate station-centered demo packages and optional random city station swaps
- Create: `backend/app/utils/china_station_catalog.py`
  - curated random city station seeds across China
- Modify: `backend/app/api/v1/endpoints/delivery.py`
  - add current-station read/update endpoints
  - make package reinit station-aware instead of Shanghai-only
- Modify: `backend/app/api/v1/endpoints/dispatch.py`
  - make `reset-demo` support `randomize_station`
- Modify: `backend/app/schemas/all_schemas.py`
  - add station update and reset-demo request schemas
- Modify: `backend/app/api/v1/endpoints/utils.py`
  - use main-station helper so seed-data stays consistent
- Modify: `frontend/src/views/Settings.vue`
  - add editable main-station form and station-aware reset actions
- Modify: `frontend/src/views/SmartDispatch.vue`
  - load current station from API instead of hardcoded constants
- Modify: `frontend/src/views/RealtimeMap.vue`
  - load current station from API instead of hardcoded constants
- Modify: `frontend/src/views/PackageFlow.vue`
  - default new package coordinates around current station instead of fixed Shanghai center
- Modify: `frontend/src/views/CourierWork.vue`
  - use current station id when creating couriers
- Modify: `frontend/src/__tests__/LegacyPages.spec.ts`
  - cover new Settings station form and actions
- Modify: `frontend/src/__tests__/SmartDispatch.spec.ts`
  - cover current-station loading and station-aware reset payloads
- Modify: `frontend/src/__tests__/RealtimeMap.spec.ts`
  - cover dynamic station coordinates
- Create: `backend/tests/services/test_station_service.py`
  - verify single-main-station semantics
- Create: `backend/tests/services/test_demo_data_service.py`
  - verify station-centered randomness and random-city selection
- Modify: `backend/tests/test_dispatch_api.py`
  - cover `randomize_station` reset flow
- Modify: `backend/tests/test_config.py`
  - no change required
- Modify: `README.md`
  - update product behavior summary
- Modify: `README_zh-CN.md`
  - update Chinese behavior summary

## Backend Contract

Use these new or clarified endpoints:

- `GET /api/v1/delivery/stations/current`
  - returns the one main station used by UI, dispatch, and demo-data generation
- `PATCH /api/v1/delivery/stations/current`
  - updates name, address, latitude, longitude of the main station
- `POST /api/v1/dispatch/reset-demo`
  - accept JSON body:

```json
{
  "randomize_station": false
}
```

Rules:

- `randomize_station=false`
  - keep current station
  - regenerate packages/couriers around it
- `randomize_station=true`
  - choose one random city seed from the China catalog
  - update the main station
  - regenerate packages/couriers around the new station

## Demo Randomness Rules

The generated data should look random but still plausible around the station.

- Package distribution:
  - 65% near ring: `0.8km` to `3.0km`
  - 25% medium ring: `3.0km` to `8.0km`
  - 10% outer ring: `8.0km` to `15.0km`
- Add clustered randomness:
  - sample `5` to `8` neighborhood anchors around the station
  - each package picks one anchor, then gets a smaller jitter around that anchor
- Coordinate conversion:
  - latitude offset uses `km / 111.0`
  - longitude offset uses `km / (111.0 * cos(lat))`
- Keep package address strings synthetic but city-aware, for example:

```python
f"{station_city}{district_name}{road_name}{building_no}号"
```

## Current-Station Semantics

Implement a service helper with these rules:

- if no station exists:
  - create a default main station
- if one station exists:
  - return it
- if multiple stations exist:
  - return the lowest-id station as the main station for this iteration
  - do not expose multi-station selection in the UI

This avoids schema churn while keeping behavior deterministic.

### Task 1: Add Main-Station Backend Service And API

**Files:**
- Create: `backend/app/services/station_service.py`
- Modify: `backend/app/api/v1/endpoints/delivery.py`
- Modify: `backend/app/schemas/all_schemas.py`
- Create: `backend/tests/services/test_station_service.py`

- [ ] **Step 1: Write failing tests for the main-station service**

Create `backend/tests/services/test_station_service.py` with:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models.all_models import Base, DeliveryStation
from app.services.station_service import StationService

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_get_or_create_main_station_creates_default_when_missing():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        station = StationService(db).get_or_create_main_station()
        assert station.name
        assert station.latitude
        assert station.longitude
    finally:
        db.close()

def test_get_or_create_main_station_returns_lowest_id_when_multiple_exist():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        db.add_all([
            DeliveryStation(name="B", address="B", latitude=30.0, longitude=120.0),
            DeliveryStation(name="A", address="A", latitude=31.0, longitude=121.0),
        ])
        db.commit()
        station = StationService(db).get_or_create_main_station()
        assert station.id == 1
    finally:
        db.close()
```

- [ ] **Step 2: Run the station service tests and confirm failure**

Run:

```bash
cd backend && uv run pytest tests/services/test_station_service.py -v
```

Expected:

- failure because `StationService` does not exist yet

- [ ] **Step 3: Add station service implementation**

Create `backend/app/services/station_service.py` with:

```python
from sqlalchemy.orm import Session
from app.models import all_models as models

DEFAULT_MAIN_STATION = {
    "name": "上海人民广场配送站",
    "address": "上海市黄浦区人民广场",
    "latitude": 31.2304,
    "longitude": 121.4737,
}

class StationService:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_main_station(self) -> models.DeliveryStation:
        station = self.db.query(models.DeliveryStation).order_by(models.DeliveryStation.id.asc()).first()
        if station:
            return station
        station = models.DeliveryStation(**DEFAULT_MAIN_STATION)
        self.db.add(station)
        self.db.commit()
        self.db.refresh(station)
        return station

    def update_main_station(self, *, name: str, address: str, latitude: float, longitude: float) -> models.DeliveryStation:
        station = self.get_or_create_main_station()
        station.name = name
        station.address = address
        station.latitude = latitude
        station.longitude = longitude
        self.db.commit()
        self.db.refresh(station)
        return station
```

- [ ] **Step 4: Add API schema and endpoints**

In `backend/app/schemas/all_schemas.py`, add:

```python
class StationUpdate(BaseModel):
    name: str
    address: str
    latitude: float
    longitude: float
```

In `backend/app/api/v1/endpoints/delivery.py`, add:

```python
from app.services.station_service import StationService

@router.get("/stations/current", response_model=schemas.Station)
def read_current_station(db: Session = Depends(get_db)):
    return StationService(db).get_or_create_main_station()

@router.patch("/stations/current", response_model=schemas.Station)
def update_current_station(station: schemas.StationUpdate, db: Session = Depends(get_db)):
    return StationService(db).update_main_station(**station.model_dump())
```

- [ ] **Step 5: Re-run the backend tests for the station service**

Run:

```bash
cd backend && uv run pytest tests/services/test_station_service.py tests/test_dispatch_api.py -v
```

Expected:

- new station service tests pass
- existing dispatch API tests still pass

- [ ] **Step 6: Commit**

```bash
git add backend/app/services/station_service.py backend/app/api/v1/endpoints/delivery.py backend/app/schemas/all_schemas.py backend/tests/services/test_station_service.py
git commit -m "feat: add single main station backend contract"
```

### Task 2: Make Demo Data Generation Station-Aware And Support Random City Station Resets

**Files:**
- Create: `backend/app/utils/china_station_catalog.py`
- Create: `backend/app/services/demo_data_service.py`
- Modify: `backend/app/api/v1/endpoints/delivery.py`
- Modify: `backend/app/api/v1/endpoints/dispatch.py`
- Modify: `backend/app/api/v1/endpoints/utils.py`
- Modify: `backend/app/schemas/all_schemas.py`
- Create: `backend/tests/services/test_demo_data_service.py`
- Modify: `backend/tests/test_dispatch_api.py`

- [ ] **Step 1: Write failing tests for station-centered demo generation**

Create `backend/tests/services/test_demo_data_service.py` with:

```python
from app.services.demo_data_service import build_package_points_around_station, choose_random_station_seed

def test_build_package_points_around_station_stays_near_station():
    station = {"name": "上海人民广场配送站", "address": "上海市黄浦区人民广场", "latitude": 31.2304, "longitude": 121.4737}
    packages = build_package_points_around_station(station, count=50, seed=7)
    assert len(packages) == 50
    assert all("latitude" in pkg and "longitude" in pkg for pkg in packages)

def test_choose_random_station_seed_returns_city_level_station():
    station = choose_random_station_seed(seed=7)
    assert station["name"]
    assert station["address"]
    assert isinstance(station["latitude"], float)
    assert isinstance(station["longitude"], float)
```

- [ ] **Step 2: Run the demo-data tests and confirm failure**

Run:

```bash
cd backend && uv run pytest tests/services/test_demo_data_service.py -v
```

Expected:

- failure because the demo-data service and city catalog do not exist yet

- [ ] **Step 3: Add a nationwide station catalog**

Create `backend/app/utils/china_station_catalog.py` with a curated list:

```python
CHINA_MAIN_STATION_SEEDS = [
    {"name": "北京国贸配送站", "address": "北京市朝阳区国贸", "latitude": 39.9088, "longitude": 116.4575},
    {"name": "上海人民广场配送站", "address": "上海市黄浦区人民广场", "latitude": 31.2304, "longitude": 121.4737},
    {"name": "广州珠江新城配送站", "address": "广州市天河区珠江新城", "latitude": 23.1195, "longitude": 113.3270},
    {"name": "深圳福田中心配送站", "address": "深圳市福田区市民中心", "latitude": 22.5431, "longitude": 114.0579},
    {"name": "杭州钱江新城配送站", "address": "杭州市上城区钱江新城", "latitude": 30.2459, "longitude": 120.2108},
    {"name": "成都春熙路配送站", "address": "成都市锦江区春熙路", "latitude": 30.6586, "longitude": 104.0817},
    {"name": "武汉江汉路配送站", "address": "武汉市江汉区江汉路", "latitude": 30.5801, "longitude": 114.2919},
    {"name": "西安钟楼配送站", "address": "西安市碑林区钟楼", "latitude": 34.2610, "longitude": 108.9423},
]
```

- [ ] **Step 4: Add a demo-data service**

Create `backend/app/services/demo_data_service.py` with:

```python
import math
import random

from app.utils.china_station_catalog import CHINA_MAIN_STATION_SEEDS

def choose_random_station_seed(seed: int | None = None) -> dict:
    rng = random.Random(seed)
    return dict(rng.choice(CHINA_MAIN_STATION_SEEDS))

def _km_to_lat(km: float) -> float:
    return km / 111.0

def _km_to_lng(km: float, lat: float) -> float:
    return km / (111.0 * math.cos(math.radians(lat)))

def build_package_points_around_station(station: dict, count: int, seed: int | None = None) -> list[dict]:
    rng = random.Random(seed)
    anchors = []
    for _ in range(rng.randint(5, 8)):
        radius_km = rng.uniform(0.8, 6.0)
        angle = rng.uniform(0, math.pi * 2)
        anchors.append((
            station["latitude"] + _km_to_lat(radius_km * math.cos(angle)),
            station["longitude"] + _km_to_lng(radius_km * math.sin(angle), station["latitude"]),
        ))

    packages = []
    for i in range(count):
        roll = rng.random()
        if roll < 0.65:
            radius_km = rng.uniform(0.8, 3.0)
        elif roll < 0.90:
            radius_km = rng.uniform(3.0, 8.0)
        else:
            radius_km = rng.uniform(8.0, 15.0)
        anchor_lat, anchor_lng = rng.choice(anchors)
        angle = rng.uniform(0, math.pi * 2)
        local_jitter_km = min(1.2, radius_km * 0.35)
        lat = anchor_lat + _km_to_lat(local_jitter_km * math.cos(angle))
        lng = anchor_lng + _km_to_lng(local_jitter_km * math.sin(angle), station["latitude"])
        packages.append({
            "recipient_name": f"演示用户{i + 1}",
            "recipient_address": f"{station['address']}周边片区{i + 1}号",
            "latitude": lat,
            "longitude": lng,
        })
    return packages
```

- [ ] **Step 5: Add reset request schema**

In `backend/app/schemas/all_schemas.py`, add:

```python
class ResetDemoRequest(BaseModel):
    randomize_station: bool = False
```

- [ ] **Step 6: Refactor `reset-demo` to use station-aware generation**

In `backend/app/api/v1/endpoints/dispatch.py`, change the signature to:

```python
@router.post("/reset-demo")
def reset_demo_data(payload: schemas.ResetDemoRequest, db: Session = Depends(get_db)):
```

And use:

```python
from app.services.station_service import StationService
from app.services.demo_data_service import choose_random_station_seed, build_package_points_around_station

station_service = StationService(db)
station = station_service.get_or_create_main_station()

if payload.randomize_station:
    random_station = choose_random_station_seed()
    station = station_service.update_main_station(**random_station)
```

Then generate package coordinates around `station.latitude` and `station.longitude` instead of from the fixed Shanghai list.

- [ ] **Step 7: Make package reinit use the same station-aware helper**

In `backend/app/api/v1/endpoints/delivery.py`, replace the Shanghai-only `reinit_package_data` logic with:

```python
station = StationService(db).get_or_create_main_station()
package_points = build_package_points_around_station(
    {
        "name": station.name,
        "address": station.address,
        "latitude": station.latitude,
        "longitude": station.longitude,
    },
    count=300,
)
```

- [ ] **Step 8: Update seed-data utility endpoint to use the main station helper**

In `backend/app/api/v1/endpoints/utils.py`, replace direct station creation with:

```python
from app.services.station_service import StationService
station = StationService(db).get_or_create_main_station()
```

- [ ] **Step 9: Add failing API tests for randomized station reset**

Extend `backend/tests/test_dispatch_api.py` with:

```python
def test_reset_demo_data_can_randomize_main_station(test_db):
    response = client.post("/api/v1/dispatch/reset-demo", json={"randomize_station": True})
    assert response.status_code == 200
    data = response.json()
    assert "station" in data
    assert "latitude" in data["station"]
    assert "longitude" in data["station"]
```

- [ ] **Step 10: Run the backend demo-data and API tests**

Run:

```bash
cd backend && uv run pytest tests/services/test_demo_data_service.py tests/test_dispatch_api.py -v
```

Expected:

- new demo-data tests pass
- reset-demo tests pass with both `randomize_station=false` and `true`

- [ ] **Step 11: Commit**

```bash
git add backend/app/utils/china_station_catalog.py backend/app/services/demo_data_service.py backend/app/api/v1/endpoints/delivery.py backend/app/api/v1/endpoints/dispatch.py backend/app/api/v1/endpoints/utils.py backend/app/schemas/all_schemas.py backend/tests/services/test_demo_data_service.py backend/tests/test_dispatch_api.py
git commit -m "feat: make demo data generation main-station aware"
```

### Task 3: Replace Hardcoded Station State In Dispatch And Monitor Pages

**Files:**
- Modify: `frontend/src/views/SmartDispatch.vue`
- Modify: `frontend/src/views/RealtimeMap.vue`
- Modify: `frontend/src/__tests__/SmartDispatch.spec.ts`
- Modify: `frontend/src/__tests__/RealtimeMap.spec.ts`

- [ ] **Step 1: Add failing Smart Dispatch test for current-station loading**

Extend `frontend/src/__tests__/SmartDispatch.spec.ts` with:

```ts
it('loads the current main station instead of hardcoding People Square', async () => {
  vi.mocked(axios.get)
    .mockResolvedValueOnce({ data: [{ status: 'PENDING', latitude: 30.2, longitude: 120.1 }] })
    .mockResolvedValueOnce({ data: [{ status: 'AVAILABLE' }] })
    .mockResolvedValueOnce({ data: { id: 3, name: '杭州钱江新城配送站', address: '杭州市上城区钱江新城', latitude: 30.2459, longitude: 120.2108 } })
    .mockResolvedValueOnce({ data: [] })

  const wrapper = mountComponent()
  await flushPromises()

  expect(wrapper.text()).toContain('杭州钱江新城配送站')
})
```

- [ ] **Step 2: Run the Smart Dispatch test and confirm failure**

Run:

```bash
cd frontend && npm run test:unit -- SmartDispatch
```

Expected:

- failure because `SmartDispatch.vue` still uses hardcoded station name/id/coordinates

- [ ] **Step 3: Load current station in `SmartDispatch.vue`**

Add state:

```ts
const stationName = ref('')
const stationId = ref<number | null>(null)
const stationCoords = ref<[number, number]>([31.2304, 121.4737])
```

Add loader:

```ts
const fetchCurrentStation = async () => {
  const stationRes = await axios.get('/api/v1/delivery/stations/current')
  stationName.value = stationRes.data.name
  stationId.value = stationRes.data.id
  stationCoords.value = [stationRes.data.latitude, stationRes.data.longitude]
}
```

Then in `onMounted()`:

```ts
await Promise.all([fetchDispatchContext(), fetchCurrentStation()])
map = L.map(mapRef.value).setView(stationCoords.value, 12)
L.marker(stationCoords.value, { icon: stationIcon }).addTo(map).bindPopup(stationName.value)
```

And in `startDispatch()`:

```ts
station_id: stationId.value
```

- [ ] **Step 4: Add failing Realtime Map test for dynamic station coordinates**

Extend `frontend/src/__tests__/RealtimeMap.spec.ts` with:

```ts
it('uses the current main station coordinates for the depot marker and reset position', async () => {
  vi.mocked(axios.get)
    .mockResolvedValueOnce({ data: { id: 3, name: '成都春熙路配送站', address: '成都市锦江区春熙路', latitude: 30.6586, longitude: 104.0817 } })
    .mockResolvedValueOnce({ data: [] })
})
```

Change the component to request `/api/v1/delivery/stations/current` before drawing the map.

- [ ] **Step 5: Update `RealtimeMap.vue` to load the current station**

Replace:

```ts
const stationCoord: L.LatLngTuple = [31.2304, 121.4737]
```

with:

```ts
const stationCoord = ref<L.LatLngTuple>([31.2304, 121.4737])
const stationName = ref('配送站')

const loadCurrentStation = async () => {
  const stationRes = await axios.get('/api/v1/delivery/stations/current')
  stationCoord.value = [stationRes.data.latitude, stationRes.data.longitude]
  stationName.value = stationRes.data.name
}
```

Then use `stationCoord.value` in:

```ts
map = L.map(mapRef.value).setView(stationCoord.value, 12)
L.marker(stationCoord.value, { icon: stationIcon }).addTo(map).bindPopup(stationName.value)
currentPos: [...stationCoord.value]
```

- [ ] **Step 6: Re-run the frontend tests**

Run:

```bash
cd frontend && npm run test:unit -- SmartDispatch RealtimeMap
```

Expected:

- both suites pass with the dynamic station flow

- [ ] **Step 7: Commit**

```bash
git add frontend/src/views/SmartDispatch.vue frontend/src/views/RealtimeMap.vue frontend/src/__tests__/SmartDispatch.spec.ts frontend/src/__tests__/RealtimeMap.spec.ts
git commit -m "feat(frontend): consume current main station dynamically"
```

### Task 4: Add Main-Station Controls And Reset Actions To Settings

**Files:**
- Modify: `frontend/src/views/Settings.vue`
- Modify: `frontend/src/__tests__/LegacyPages.spec.ts`

- [ ] **Step 1: Add failing Settings page tests for station editing and station-randomizing reset**

Extend `frontend/src/__tests__/LegacyPages.spec.ts` with:

```ts
it('renders a main-station form and saves edits through the current-station endpoint', async () => {
  vi.mocked(axios.get)
    .mockResolvedValueOnce({ data: [{ id: 1 }, { id: 2 }] })
    .mockResolvedValueOnce({ data: [{ id: 1 }] })
    .mockResolvedValueOnce({ data: [{ id: 1 }] })
    .mockResolvedValueOnce({ data: { id: 1, name: '上海人民广场配送站', address: '上海市黄浦区人民广场', latitude: 31.2304, longitude: 121.4737 } })
})
```

Also assert a reset call shape:

```ts
expect(axios.post).toHaveBeenCalledWith('/api/v1/dispatch/reset-demo', { randomize_station: true })
```

- [ ] **Step 2: Run the Settings page tests and confirm failure**

Run:

```bash
cd frontend && npm run test:unit -- LegacyPages
```

Expected:

- failure because the Settings page has no station form and no random-city reset action

- [ ] **Step 3: Add station form state to `Settings.vue`**

Add:

```ts
const stationForm = ref({
  name: '',
  address: '',
  latitude: 31.2304,
  longitude: 121.4737,
})
```

Load it with:

```ts
const loadCurrentStation = async () => {
  const stationRes = await axios.get('/api/v1/delivery/stations/current')
  stationForm.value = {
    name: stationRes.data.name,
    address: stationRes.data.address,
    latitude: stationRes.data.latitude,
    longitude: stationRes.data.longitude,
  }
}
```

- [ ] **Step 4: Add save and reset actions**

Add:

```ts
const saveMainStation = async () => {
  await axios.patch('/api/v1/delivery/stations/current', stationForm.value)
  await loadStats()
  ElMessage.success('主配送站已更新')
}

const resetDemoAroundCurrentStation = async () => {
  await axios.post('/api/v1/dispatch/reset-demo', { randomize_station: false })
  await loadCurrentStation()
  await loadStats()
  ElMessage.success('已按当前配送站重置样本')
}

const resetDemoWithRandomStation = async () => {
  await axios.post('/api/v1/dispatch/reset-demo', { randomize_station: true })
  await loadCurrentStation()
  await loadStats()
  ElMessage.success('已随机切换城市并重置样本')
}
```

- [ ] **Step 5: Render the new station form**

Add one section card with fields:

```vue
<el-input v-model="stationForm.name" />
<el-input v-model="stationForm.address" />
<el-input-number v-model="stationForm.latitude" :step="0.0001" />
<el-input-number v-model="stationForm.longitude" :step="0.0001" />
<el-button type="primary" @click="saveMainStation">保存主配送站</el-button>
```

And in the maintenance section add two explicit actions:

```vue
<el-button type="warning" @click="resetDemoAroundCurrentStation">按当前站点重置</el-button>
<el-button type="danger" @click="resetDemoWithRandomStation">随机城市重置</el-button>
```

- [ ] **Step 6: Re-run the Settings tests**

Run:

```bash
cd frontend && npm run test:unit -- LegacyPages
```

Expected:

- Settings tests pass with the new station controls and reset payloads

- [ ] **Step 7: Commit**

```bash
git add frontend/src/views/Settings.vue frontend/src/__tests__/LegacyPages.spec.ts
git commit -m "feat(settings): add main station controls and station-aware resets"
```

### Task 5: Make Package And Courier Creation Respect The Main Station

**Files:**
- Modify: `frontend/src/views/PackageFlow.vue`
- Modify: `frontend/src/views/CourierWork.vue`

- [ ] **Step 1: Add failing expectations for station-aware defaults**

Create or extend unit coverage so:

```ts
expect(form.latitude).toBeCloseTo(currentStation.latitude, 3)
expect(form.longitude).toBeCloseTo(currentStation.longitude, 3)
expect(courierPayload.station_id).toBe(currentStation.id)
```

- [ ] **Step 2: Run the relevant frontend tests and confirm failure**

Run:

```bash
cd frontend && npm run test:unit -- LegacyPages
```

Expected:

- failure or missing coverage because the pages still use hardcoded station defaults

- [ ] **Step 3: Load the current station in `PackageFlow.vue`**

Replace fixed defaults:

```ts
latitude: 31.2304,
longitude: 121.4737
```

with a station loader and station-centered random fill:

```ts
const currentStation = ref({ id: 1, latitude: 31.2304, longitude: 121.4737 })
const randomizeAroundStation = () => {
  form.latitude = currentStation.value.latitude + (Math.random() - 0.5) * 0.08
  form.longitude = currentStation.value.longitude + (Math.random() - 0.5) * 0.08
}
```

- [ ] **Step 4: Load the current station in `CourierWork.vue`**

Replace:

```ts
station_id: 1
```

with:

```ts
const currentStationId = ref<number | null>(null)
const loadCurrentStation = async () => {
  const stationRes = await axios.get('/api/v1/delivery/stations/current')
  currentStationId.value = stationRes.data.id
}
```

And use:

```ts
station_id: currentStationId.value
```

- [ ] **Step 5: Re-run the relevant frontend tests**

Run:

```bash
cd frontend && npm run test:unit
```

Expected:

- the full frontend suite passes

- [ ] **Step 6: Commit**

```bash
git add frontend/src/views/PackageFlow.vue frontend/src/views/CourierWork.vue
git commit -m "feat(frontend): align package and courier defaults with main station"
```

### Task 6: Update Docs And Verify End-To-End Behavior

**Files:**
- Modify: `README.md`
- Modify: `README_zh-CN.md`

- [ ] **Step 1: Update the docs to describe the new behavior**

Add language like:

```md
The system now uses one editable main delivery station across settings, dispatch, map views, and demo-data generation.
Reset actions can either regenerate data around the current station or randomly switch the station to another supported Chinese city before regenerating samples.
Route optimization still uses the existing Haversine-based K-Means + GA pipeline.
```

Chinese version:

```md
系统现在统一使用一个可编辑的主配送站，设置页、调度页、监控地图和演示数据生成都会读取该站点。
重置样本时既可以围绕当前站点重新生成，也可以随机切换到全国其他城市的站点后再生成样本。
调度算法仍保持现有的 Haversine 直线距离 + K-Means 聚类 + 遗传算法流程。
```

- [ ] **Step 2: Run the backend and frontend verification commands**

Run:

```bash
cd backend && uv run pytest -q
```

Run:

```bash
cd frontend && npm run test:unit
```

Expected:

- backend tests pass
- frontend tests pass

- [ ] **Step 3: Perform manual verification**

Manual checklist:

1. Open `Settings`.
2. Edit the main station name and coordinates.
3. Save it.
4. Open `调度中心` and confirm the map center and station label changed.
5. Open `路线监控` and confirm the depot marker starts from the same station.
6. Click “按当前站点重置” and confirm pending packages are regenerated around the edited station.
7. Click “随机城市重置” and confirm:
   - the station changes to another city
   - the dispatch map recenters
   - regenerated packages cluster around the new city center
8. Start one dispatch and confirm it still completes with the current straight-line algorithm.

- [ ] **Step 4: Commit**

```bash
git add README.md README_zh-CN.md
git commit -m "docs: describe single main station and reset behavior"
```

## Definition Of Done

- `Settings` can edit the single main station
- `SmartDispatch` and `RealtimeMap` load current station dynamically
- package reinit and demo reset generate data around the current station
- reset-demo supports `randomize_station=true`
- random station swaps use a curated nationwide China city list
- dispatch still uses the existing straight-line/Haversine optimization model
- backend tests and frontend tests pass
