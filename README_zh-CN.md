# OptiRoute-LastMile

[[English](README.md)]

这是一个基于 FastAPI + Vue 3 的末端配送调度演示系统。当前仓库的核心不是“抽象算法展示”，而是围绕单一主配送站、演示数据重置、调度执行、路线回放和历史复盘构建的完整前后端演示链路。

## 当前项目实际包含的能力

- 基于 JWT 的注册、登录和当前用户查询。
- 创建调度计划后，通过 FastAPI `BackgroundTasks` 在后台执行调度。
- 一个全局共享的“当前主配送站”，调度、监控、包裹录入、快递员录入和演示数据重置都依赖它。
- 基于内置全国城市站点目录的演示数据重置，支持随机切换城市后重建样本。
- 调度中心、路线监控、历史复盘、任务概览、运营分析、包裹数据、快递员数据、系统设置等完整页面。
- 后端与前端自动化测试。

## 当前调度流程

1. 系统读取当前主配送站。
2. 演示数据重置会先准备 300 个包裹和 10 名快递员的基础池，再抽取 100-150 个 `PENDING` 包裹和 5-10 名 `AVAILABLE` 快递员作为本次可调度样本。
3. 调用 `POST /api/v1/dispatch/plans` 创建计划后，FastAPI 会启动后台任务执行算法。
4. 后端先用自定义约束 K-Means 做包裹分区，过程中会考虑包裹重量与快递员容量。
5. 然后对每个分区运行自定义遗传算法求解 TSP 风格的访问顺序。
6. 中间结果和最终 GeoJSON 路线都会持续写回 SQLite，前端据此轮询展示和回放结果。

## 当前实现的关键事实

- 调度距离仍然基于 Haversine 直线距离，不是道路路网规划结果。
- 当前后端算法参数写死在代码中：
  - `k = min(available_couriers, pending_packages)`
  - `max_distance_from_depot = 50.0`
  - `population_size = 50`
  - `generations = 100`
- 前端当前不是一个真实的算法调参面板，实际控制权仍在后端固定配置里。
- 更新当前主站点时，如果已有历史计划，系统会先归档旧站点记录，再把新站点设为当前主站。
- `backend/seed_shanghai_data.py` 只是初始化基础上海样本，其中包裹初始状态是 `ASSIGNED`；如果你想直接在界面里发起调度，需要先点击 `重置数据`，或者调用 `/api/v1/dispatch/reset-demo`。

## 技术栈

### 后端

- FastAPI
- SQLAlchemy + SQLite
- Alembic
- NumPy
- Pydantic v2
- `uv`

### 前端

- Vue 3 + TypeScript
- Vue Router
- Pinia
- Element Plus
- Leaflet + Leaflet Ant Path
- ECharts
- Vite
- Vitest

## 仓库结构

- `backend/`：FastAPI 应用、算法实现、服务层、迁移与测试
- `frontend/`：Vue 应用、页面、路由、状态管理与测试
- `scripts/`：一键启动脚本
- `docs/`：设计文档与论文相关资料

## 安装

### 前置要求

- Python 3.11+
- Node.js 18+
- `uv`

### 后端

```bash
cd backend
uv sync
uv run alembic upgrade head
uv run python seed_shanghai_data.py
```

### 前端

```bash
cd frontend
npm install
```

## 启动项目

### 手动启动

后端：

```bash
cd backend
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir app
```

前端：

```bash
cd frontend
npm run dev
```

浏览器访问 `http://localhost:5173`。

### 一键启动

在仓库根目录执行：

```bash
bash scripts/dev-up.sh
```

新机器首次启动：

```bash
bash scripts/bootstrap-and-up.sh
```

可选端口与地址：

```bash
BACKEND_HOST=0.0.0.0 BACKEND_PORT=8000 FRONTEND_HOST=0.0.0.0 FRONTEND_PORT=5173 bash scripts/dev-up.sh
```

## 推荐首次使用流程

1. 注册或登录。
2. 进入 `系统设置`，确认当前主配送站。
3. 进入 `调度中心`。
4. 点击 `重置数据`，生成本次可调度的待配送包裹和可用快递员。
5. 点击 `开始AI调度`。
6. 在 `路线监控`、`调度历史`、`任务概览` 和 `运营分析` 中查看结果。

## 主要页面

- `调度中心`：发起调度、查看样本数量、在地图中查看结果
- `路线监控`：按步骤回放最新一次完成的路线结果
- `调度历史`：比较最多 3 个已完成计划并查看路线详情
- `任务概览`：查看引导步骤与近期运营摘要
- `运营分析`：查看 KPI、近期路线趋势和估算节省
- `包裹数据`：搜索和新增包裹
- `快递员数据`：查看和新增快递员
- `系统设置`：维护主站点、重建包裹样本、清空历史、执行站点感知的演示数据重置

## 主要 API

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

OpenAPI 地址：`http://localhost:8000/api/v1/openapi.json`

## 测试

后端：

```bash
cd backend
uv run pytest
```

前端：

```bash
cd frontend
npm run test:unit
npm run build
```

## 当前限制

- 当前优化结果属于演示级启发式方案，不是生产级路径规划引擎。
- 后端当前使用 SQLite 和轮询式结果持久化，而不是 Redis / WebSocket 实时推送。
- `openrouteservice`、`redis`、`celery`、`scikit-learn` 等依赖已经在环境中，但当前活跃调度链路仍是仓库内自定义 K-Means + GA 实现。
- 运营分析中包含明确标注的估算值，不全部是实际物流成本统计。

## 故障排查

如果遇到 `no such table` 或 `no such column` 这类数据库结构错误：

```bash
cd backend
rm -f sql_app.db sql_app.db-shm sql_app.db-wal
uv run alembic upgrade head
uv run python seed_shanghai_data.py
```

如果前端连不上后端，先确认 FastAPI 是否运行在 `http://localhost:8000`，因为开发环境下 Vite 会把 `/api/*` 代理到这个地址。

## 补充说明

- [backend/README.md](backend/README.md)：后端说明
- [frontend/README.md](frontend/README.md)：前端说明
- [docs/快递末端配送系统设计文档.md](docs/快递末端配送系统设计文档.md)：设计导向的项目文档
