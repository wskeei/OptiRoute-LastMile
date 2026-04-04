# Frontend

This directory contains the Vue 3 frontend for SmartDispatch-AI.

## Stack

- Vue 3 + TypeScript
- Vue Router
- Pinia
- Element Plus
- Leaflet + Leaflet Ant Path
- ECharts
- Vite

## Available Pages

- `Dashboard`: overview cards and recent dispatch trends
- `SmartDispatch`: dispatch trigger page with map-based route visualization
- `PackageFlow`: package list and lifecycle view
- `CourierWork`: courier list and workload view
- `RealtimeMap`: latest plan replay and courier status view
- `Analytics`: KPI and workload analysis
- `RouteHistory`: completed-plan comparison and route metrics
- `Settings`: local algorithm defaults, system stats, history reset, package reinitialization

## Development

```bash
npm install
npm run dev
```

The dev server proxies `/api/*` requests to `http://localhost:8000`, so the FastAPI backend should be running locally during development.

## Current Notes

- The dispatch page exposes `k` and GA generation sliders for demonstration.
- The settings page stores values in browser `localStorage`.
- The current backend dispatch service still uses fixed algorithm values and does not consume those frontend settings yet.
