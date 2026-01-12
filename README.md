# AI-Powered Last-Mile Delivery Optimization System

This project is a full-stack application designed to optimize last-mile delivery routes for courier services. It uses a combination of K-Means clustering to partition delivery zones and a Genetic Algorithm (GA) to solve the Traveling Salesperson Problem (TSP) for each zone, minimizing total delivery distance and time.

The system is composed of a Python FastAPI backend that handles the core algorithmic logic and a Vue.js frontend that provides a modern, interactive dashboard for managing and visualizing the entire dispatch process.

![System Screenshot](https://i.imgur.com/your-screenshot.png) <!-- It's recommended to add a screenshot of the running application -->

## 🚀 Features

- **AI-Powered Dispatch**: Automatically groups packages into clusters and calculates the optimal delivery route for each courier.
- **Interactive Map Dashboard**: Visualize package locations, courier assignments, and optimized routes on a Leaflet map.
- **Real-time Progress**: Monitor the status of the optimization algorithm from data processing to final results.
- **Full-Stack Management**:
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

# [Optional] Seed the database with test data
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

2.  **Start the Frontend Server**:
    ```bash
    cd frontend
    npm run dev
    ```
    The application will be accessible at `http://localhost:5173`.

3.  **Usage**:
    - Navigate to **AI调度中心** (AI Dispatch Center)
    - Click **"🚀 开始AI调度"** to start the intelligent dispatch
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
