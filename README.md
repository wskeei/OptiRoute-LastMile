# SmartDispatch-AI: Intelligent Last-Mile Delivery System

[[中文文档](README_zh-CN.md)]
> *AI-Driven Logistics Optimization with Real-World Constraints*

**SmartDispatch-AI** is a comprehensive full-stack solution designed to tackle the "Last Mile" delivery challenge. By synergizing **K-Means Clustering** for region partitioning and **Genetic Algorithms (GA)** for route optimization, it generates highly efficient delivery plans that respect potential real-world constraints like courier capacity.

The system features a **FastAPI** backend for high-performance computing and a **Vue 3** frontend for an immersive, data-rich user experience.

![System Screenshot](https://i.imgur.com/your-screenshot.png)

## 🚀 Key Features

### 🧠 Intelligent Core
- **Hybrid Algorithm Engine**: Combines **Constrained K-Means** (balanced clustering) with **Genetic Algorithms** (TSP solver) to minimize total travel distance and cost.
- **Dynamic Capacity Management**: Automatically adjusts courier loads based on real-time package volume and individual weight/volume constraints (e.g., max 150kg).
- **Real-World Data Simulation**: Integrated with real geographic data from **Shanghai**, generating realistic package addresses and coordinates for testing.

### 🖥️ Interactive Visualization
- **Realtime Monitor**: Watch couriers move along their optimized paths in real-time, with dynamic load tracking and interactive popups.
- **Smart Dispatch Center**: Visual progress of the algorithm evolution, showing how routes improve generation by generation.
- **Ant-Path Animation**: Animated path visualizations on Leaflet maps to clearly indicate delivery direction and flow.

### 📊 Comprehensive Management
- **One-Click Dispatch**: Trigger complex optimization tasks with a single button.
- **Data Analytics**: Insightful dashboards showing courier ranking, efficiency trends, and cost-saving metrics.
- **Lifecycle Tracking**: Full management of package states from `PENDING` -> `ASSIGNED` -> `IN_TRANSIT` -> `DELIVERED`.
- **System Control**: Reset demo data or clear history instantly via system settings.
    - **Dashboard**: Get a quick overview of daily stats, efficiency trends, and courier performance.
    - **Package Management**: Track packages through their entire lifecycle (pending, in-transit, delivered).
    - **Courier Workbench**: Monitor courier status, workload, and performance analytics.
    - **Analytics & History**: Review past optimization results and analyze performance metrics.
- **Configurable**: Easily adjust algorithm parameters (K-value, generations) directly from the UI.

## 🛠️ Technology Stack

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Language**: Python 3.11
- **Database**: [SQLite](https://www.sqlite.org/) (for simplicity, via SQLAlchemy)
- **Migrations**: [Alembic](https://alembic.sqlalchemy.org/)
- **Algorithms**:
    - [scikit-learn](https://scikit-learn.org/) for K-Means clustering.
    - Custom-built Genetic Algorithm using NumPy.
- **Package Manager**: [uv](https://github.com/astral-sh/uv)

### Frontend
- **Framework**: [Vue 3](https://vuejs.org/) (Composition API with `<script setup>`)
- **Language**: TypeScript
- **UI Toolkit**: [Element Plus](https://element-plus.org/)
- **Mapping**: [Leaflet](https://leafletjs.com/) + [Leaflet Ant Path](https://github.com/rubenspgcavalcante/leaflet-ant-path)
- **Charting**: [ECharts](https://echarts.apache.org/)
- **State Management**: [Pinia](https://pinia.vuejs.org/)
- **Build Tool**: [Vite](https://vitejs.dev/)
- **Design**: Glassmorphism with gradient backgrounds

## ⚙️ Setup and Installation

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- `uv` installed (`pip install uv`)

### 1. Backend Setup

```bash
# Navigate to the backend directory
cd backend

# Install dependencies (creates virtual environment automatically)
uv sync

# Apply database migrations
uv run alembic upgrade head

# Initialize database with required data (stations, couriers, packages)
uv run python seed_shanghai_data.py
```

### 2. Frontend Setup

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install
```

## 🚀 Running the Application

1.  **Start the Backend Server**:
    ```bash
    cd backend
    uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ```
    The API will be available at `http://localhost:8000`.

    > **Note**: On Windows, if the server keeps restarting due to SQLite file changes, use:
    > ```bash
    > uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir app
    > ```

2.  **Start the Frontend Server**:
    ```bash
    cd frontend
    npm run dev
    ```
    The application will be accessible at `http://localhost:5173`.

3.  **First-Time Usage**:
    - Navigate to **AI调度中心** (AI Dispatch Center)
    - Click **"🔄 重置演示数据"** (Reset Demo Data) to initialize random packages and couriers
    - Click **"🚀 开始AI调度"** (Start AI Dispatch) to run the optimization
    - Watch the algorithm progress through K-Means clustering and genetic algorithm optimization
    - View the optimized routes visualized on the map with animated paths

## 🎨 Design Features

- **Glassmorphism UI**: Semi-transparent cards with backdrop blur effects
- **Gradient Backgrounds**: Modern blue-purple gradient theme
- **8 Core Pages**: Dashboard, AI Dispatch Center, Package Flow, Courier Workbench, Real-time Monitor, Analytics, Route History, Settings
- **Animated Route Visualization**: Ant-path animations showing delivery direction
- **Real-time Data**: Live updates from backend APIs

---
*This project was developed with assistance from Claude Sonnet 4.5.*
