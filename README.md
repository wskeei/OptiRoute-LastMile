# OptiRoute-LastMile

[[中文文档](README_zh-CN.md)]

An intelligent last-mile delivery demo system built with FastAPI + Vue 3. The current repository is centered on a single editable main station, demo-data driven dispatch runs, and a two-stage route optimization flow based on constrained K-Means and a custom genetic algorithm.

## What The Project Currently Includes

- JWT-based registration and login.
- A dispatch workflow that creates plans, runs optimization in a FastAPI background task, and persists route geometry for replay.
- A single "current main station" shared by dispatch, monitoring, package creation, courier creation, and demo reset.
- Station-aware demo data reset, including a random-city mode based on a built-in China station catalog.
- Operational pages for dispatch, monitoring, history review, analytics, package data, courier data, and settings.
- Backend and frontend automated tests.

## Current Dispatch Flow

1. The system loads the current main station.
2. Demo reset prepares a pool of 300 packages and 10 couriers, then samples 100-150 `PENDING` packages and 5-10 `AVAILABLE` couriers for an actual run.
3. Creating a plan at `POST /api/v1/dispatch/plans` starts a FastAPI `BackgroundTasks` job.
4. Pending packages are partitioned with custom constrained K-Means, using package weight and courier capacity.
5. Each cluster is solved with a custom GA-TSP route search.
6. Intermediate and final route GeoJSON is written back to SQLite so the frontend can poll and replay results.

## Current Implementation Facts

- Dispatch distance is based on Haversine straight-line distance, not real road-network routing.
- The active backend code uses fixed algorithm settings:
  - `k = min(available_couriers, pending_packages)`
  - `max_distance_from_depot = 50.0`
  - `population_size = 50`
  - `generations = 100`
- The frontend no longer acts as a true tuning surface for these parameters.
- Updating the current main station preserves historical plan context by archiving the previous station record when needed.
- `backend/seed_shanghai_data.py` creates baseline Shanghai data, but seeded packages start as `ASSIGNED`. To get dispatch-ready samples in the UI, use `Reset Data` or call `/api/v1/dispatch/reset-demo`.

## Stack

### Backend

- FastAPI
- SQLAlchemy + SQLite
- Alembic
- NumPy
- Pydantic v2
- `uv`

### Frontend

- Vue 3 + TypeScript
- Vue Router
- Pinia
- Element Plus
- Leaflet + Leaflet Ant Path
- ECharts
- Vite
- Vitest

## Repository Layout

- `backend/`: FastAPI app, algorithms, services, migrations, tests
- `frontend/`: Vue app, views, router, store, tests
- `scripts/`: one-command startup helpers
- `docs/`: design and thesis-oriented project documents

## Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- `uv`

### Backend

```bash
cd backend
uv sync
uv run alembic upgrade head
uv run python seed_shanghai_data.py
```

### Frontend

```bash
cd frontend
npm install
```

## Start The App

### Manual Start

Backend:

```bash
cd backend
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir app
```

Frontend:

```bash
cd frontend
npm run dev
```

Open `http://localhost:5173`.

### One-Command Start

From the repository root:

```bash
bash scripts/dev-up.sh
```

First-time setup on a new machine:

```bash
bash scripts/bootstrap-and-up.sh
```

Optional ports/hosts:

```bash
BACKEND_HOST=0.0.0.0 BACKEND_PORT=8000 FRONTEND_HOST=0.0.0.0 FRONTEND_PORT=5173 bash scripts/dev-up.sh
```

## Recommended First-Run Workflow

1. Register or log in.
2. Open `Settings` and confirm the current main station.
3. Open `Dispatch`.
4. Click `Reset Data` to create dispatch-ready pending packages and available couriers.
5. Click `Start AI Dispatch`.
6. Review results in `Monitor`, `History`, `Dashboard`, and `Analytics`.

## Main Pages

- `Dispatch`: launch a run, inspect current sample counts, and view route output on the map
- `Monitor`: replay the newest completed route set step by step
- `History`: compare up to three completed plans and inspect route-level details
- `Dashboard`: view onboarding guidance and recent operational summaries
- `Analytics`: inspect KPI cards, recent route trends, and estimated savings
- `Packages`: search and create package records
- `Couriers`: browse and create courier records
- `Settings`: maintain the main station, reinitialize packages, clear history, and run station-aware demo resets

## Key API Surface

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `GET /api/v1/delivery/stations/current`
- `PATCH /api/v1/delivery/stations/current`
- `GET /api/v1/delivery/packages`
- `POST /api/v1/delivery/packages/reinit`
- `GET /api/v1/delivery/couriers`
- `POST /api/v1/dispatch/plans`
- `GET /api/v1/dispatch/plans`
- `GET /api/v1/dispatch/plans/{plan_id}/routes`
- `POST /api/v1/dispatch/reset-demo`
- `DELETE /api/v1/dispatch/plans/all`
- `GET /api/v1/stats/dashboard`
- `GET /api/v1/stats/courier-ranking`

OpenAPI is exposed at `http://localhost:8000/api/v1/openapi.json`.

## Testing

Backend:

```bash
cd backend
uv run pytest
```

Frontend:

```bash
cd frontend
npm run test:unit
npm run build
```

## Current Limitations

- The optimization result is a heuristic demo, not a production-grade routing engine.
- The backend uses SQLite and polling-friendly persistence rather than Redis-backed realtime streaming or WebSockets.
- Dependencies such as `openrouteservice`, `redis`, `celery`, and `scikit-learn` exist in the backend environment, but the active dispatch path is still the in-repo custom K-Means + GA implementation.
- Demo statistics in analytics include explicit estimates, not only measured ground-truth logistics cost data.

## Troubleshooting

If you see schema errors such as `no such table` or `no such column`:

```bash
cd backend
rm -f sql_app.db sql_app.db-shm sql_app.db-wal
uv run alembic upgrade head
uv run python seed_shanghai_data.py
```

If the frontend cannot reach the backend, make sure the FastAPI app is running on `http://localhost:8000` because Vite proxies `/api/*` there during development.

## Additional Notes

- [backend/README.md](backend/README.md): backend-specific summary
- [frontend/README.md](frontend/README.md): frontend-specific summary
- [docs/快递末端配送系统设计文档.md](docs/快递末端配送系统设计文档.md): design-oriented project document
