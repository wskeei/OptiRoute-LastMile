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
- **Mapping**: [Leaflet](https://leafletjs.com/)
- **Charting**: [ECharts](https://echarts.apache.org/)
- **State Management**: [Pinia](https://pinia.vuejs.org/)
- **Build Tool**: [Vite](https://vitejs.dev/)

## ⚙️ Setup and Installation

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- `uv` installed (`pip install uv`)

### 1. Backend Setup

```bash
# Navigate to the backend directory
cd backend

# Create a virtual environment
uv venv

# Activate the virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt

# Apply database migrations
alembic upgrade head

# [Optional] Seed the database with test data
# Start the server first, then run this in a separate terminal
curl -X POST http://localhost:8000/api/v1/utils/seed-data
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
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ```
    The API will be available at `http://localhost:8000`.

2.  **Start the Frontend Server**:
    ```bash
    cd frontend
    npm run dev
    ```
    The application will be accessible at `http://localhost:5173`.

3.  **Usage**:
    - The application will automatically connect to the backend and seed test data.
    - Navigate to the **AI Dispatch Center**.
    - Click **"Start Intelligent Dispatch"** to see the algorithm in action. The map will update with the optimized routes.

---
*This project was developed with assistance from a Gemini agent.*
