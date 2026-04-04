# Backend

This directory contains the FastAPI backend for SmartDispatch-AI.

## Responsibilities

- expose authentication, delivery, dispatch, and stats APIs
- persist stations, couriers, packages, plans, and routes with SQLAlchemy + SQLite
- run the dispatch workflow in a background task
- store intermediate and final route geometry for frontend visualization

## Algorithm Entry Points

- `app/services/dispatch_service.py`: orchestration of the dispatch pipeline
- `app/core/algorithms/kmeans.py`: custom constrained K-Means implementation
- `app/core/algorithms/genetic.py`: custom GA-based TSP solver

## Current Dispatch Pipeline

1. load pending packages and available couriers
2. set `k = min(available_couriers, pending_packages)`
3. run constrained K-Means with package weights and courier capacities
4. run GA route optimization per cluster
5. persist routes and assign packages

Current fixed values in code:

- `max_distance_from_depot = 50.0`
- `population_size = 50`
- `generations = 100`

## Development

```bash
uv sync
uv run alembic upgrade head
uv run python seed_shanghai_data.py
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
