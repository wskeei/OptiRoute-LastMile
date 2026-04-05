# SmartDispatch-AI: Intelligent Last-Mile Delivery System

[[中文文档](README_zh-CN.md)]
> *AI-driven last-mile dispatch built around constrained clustering and route search*

**SmartDispatch-AI** is a full-stack demo system for last-mile delivery planning. The current optimization pipeline uses a **two-stage heuristic**:

1. **Constrained K-Means** partitions pending packages into courier-sized regions.
2. A **custom Genetic Algorithm (GA)** solves the delivery order inside each region as a TSP-style route.

The backend is built with **FastAPI** and the frontend with **Vue 3**, focusing on route visualization, dispatch history, courier workload views, and demo-data driven experimentation.

## Key Features

### Intelligent Core
- **Hybrid optimization pipeline**: constrained K-Means for spatial partitioning, then GA-based route optimization for each cluster.
- **Capacity-aware assignment**: package weights and courier capacity limits are considered during clustering.
- **Depot-aware clustering**: cluster centers are initialized around the station and constrained by maximum distance from the depot.
- **Improved GA search**: the route solver includes tournament selection, order crossover, swap mutation, elite retention, adaptive mutation, and a `2-opt` local search pass.

### Visualization and Operations
- **Smart Dispatch Center**: trigger a dispatch run, inspect optimization progress, and view generated routes on a map.
- **Realtime Map**: replay the latest dispatch result with route overlays and courier status cards.
- **Analytics and History**: review completed plans, compare route metrics, and inspect courier workload trends.
- **Single editable main station**: settings, dispatch, realtime monitoring, package creation, courier creation, and demo-data generation all read the same current depot.
- **System actions**: reset demo data around the current depot, randomly switch to another supported Chinese city before regenerating samples, clear dispatch history, and inspect package or courier records from the UI.

## Current Algorithm Behavior

The current backend implementation uses fixed runtime settings inside the dispatch service:

- `k = min(available_couriers, pending_packages)`
- constrained K-Means with `max_distance_from_depot = 50.0`
- GA with `population_size = 50`
- GA with `generations = 100`

The dispatch pipeline still uses straight-line Haversine distance inside the existing constrained K-Means + GA flow. The settings page now manages the single main delivery station and station-aware demo reset actions; it does not expose multi-station selection or reintroduce road-network routing.

## Technology Stack

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Language**: Python 3.11+
- **Database**: [SQLite](https://www.sqlite.org/) via SQLAlchemy
- **Migrations**: [Alembic](https://alembic.sqlalchemy.org/)
- **Algorithms**:
  - Custom constrained K-Means implementation using NumPy and Haversine distance
  - Custom GA-based TSP solver using NumPy
- **Package Manager**: [uv](https://github.com/astral-sh/uv)

Note: `scikit-learn` is still listed as a dependency, but the current dispatch flow does not call `sklearn.cluster.KMeans`.

### Frontend
- **Framework**: [Vue 3](https://vuejs.org/) with `<script setup>`
- **Language**: TypeScript
- **UI Toolkit**: [Element Plus](https://element-plus.org/)
- **Mapping**: [Leaflet](https://leafletjs.com/) + [Leaflet Ant Path](https://github.com/rubenspgcavalcante/leaflet-ant-path)
- **Charting**: [ECharts](https://echarts.apache.org/)
- **State Management**: [Pinia](https://pinia.vuejs.org/)
- **Build Tool**: [Vite](https://vitejs.dev/)

## Setup and Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- `uv` installed (`pip install uv`)

### 1. Backend Setup

```bash
cd backend
uv sync
uv run alembic upgrade head
uv run python seed_shanghai_data.py
```

### 2. Frontend Setup

```bash
cd frontend
npm install
```

### Linux / Cross-OS Migration Notes

If this repository was copied from a Windows machine, do not reuse the runtime artifacts directly on Linux:

```bash
rm -f backend/sql_app.db backend/sql_app.db-shm backend/sql_app.db-wal
rm -rf frontend/node_modules
cd frontend && npm install
```

The frontend npm scripts call local CLIs through `node`, so they do not rely on executable bits preserved from another OS.

### One-Command Startup

From the repository root:

```bash
# Reset DB, migrate, seed demo data, start backend + frontend
bash scripts/dev-up.sh

# First-time setup on a new machine
bash scripts/bootstrap-and-up.sh
```

Optional environment variables:

```bash
BACKEND_HOST=0.0.0.0 BACKEND_PORT=8000 FRONTEND_HOST=0.0.0.0 FRONTEND_PORT=5173 bash scripts/dev-up.sh
```

## Running the Application

1. Start the backend:
   ```bash
   cd backend
   uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
2. Start the frontend:
   ```bash
   cd frontend
   npm run dev
   ```
3. Open `http://localhost:5173`, log in or register, then:
   - optionally open `设置` and edit the main delivery station
   - go to `AI调度中心`
   - click `重置数据`, or use `设置` to reset around the current station / randomize to another supported Chinese city
   - click `开始AI调度`
   - watch routes appear while the backend updates plan progress

## Repository Notes

- [backend/README.md](backend/README.md): backend service summary and algorithm entry points
- [frontend/README.md](frontend/README.md): frontend app summary and page map
- [docs/快递末端配送系统设计文档.md](docs/快递末端配送系统设计文档.md): design-oriented project document

## Troubleshooting

### Database Schema Errors

If you hit errors such as `no such column` or `no such table`:

```bash
cd backend
rm -f sql_app.db sql_app.db-shm sql_app.db-wal
uv run alembic upgrade head
uv run python seed_shanghai_data.py
uv run uvicorn app.main:app --reload --port 8000
```

### Backend Keeps Restarting on Windows

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir app
```

---
*This project was developed with assistance from Claude Sonnet 4.5.*
