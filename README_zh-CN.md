# SmartDispatch-AI: 智能末端物流配送系统

[[English](README.md)]
> *围绕约束聚类与路径搜索实现的末端配送调度演示系统*

**SmartDispatch-AI** 是一个面向末端配送场景的全栈演示系统。当前优化流程采用**两阶段启发式方法**：

1. 使用**约束 K-Means**将待配送包裹划分到多个快递员区域。
2. 对每个区域内的地址使用**自定义遗传算法（GA）**求解访问顺序，将其视为 TSP 风格路径。

后端基于 **FastAPI**，前端基于 **Vue 3**，重点提供调度触发、路径可视化、历史分析、快递员工作量查看和演示数据管理能力。

## 核心功能

### 智能算法核心
- **混合优化流程**：先做约束 K-Means 空间分区，再对每个聚类做 GA 路径优化。
- **容量约束分配**：聚类阶段会结合包裹重量与快递员载重上限进行分配。
- **配送站约束**：聚类中心在站点周围初始化，并受到最大离站距离约束。
- **改进型 GA 搜索**：当前路线求解器包含锦标赛选择、顺序交叉、交换变异、精英保留、自适应变异和 `2-opt` 局部搜索。

### 可视化与业务操作
- **AI 调度中心**：发起一次调度任务，查看优化进度，并在地图上展示生成的路线。
- **实时监控地图**：回放最新调度结果，展示路线覆盖和快递员状态。
- **分析与历史**：查看历史计划、路线指标对比和快递员工作量趋势。
- **系统管理操作**：支持重置演示数据、清空调度历史、查看包裹和快递员数据。

## 当前算法行为

当前后端调度服务中的运行参数是写死在代码里的：

- `k = min(available_couriers, pending_packages)`
- 约束 K-Means 的 `max_distance_from_depot = 50.0`
- GA 的 `population_size = 50`
- GA 的 `generations = 100`

前端页面目前虽然提供了 `k`、进化代数、种群大小等滑块，但这些值**还没有真正传入后端调度算法**。设置页当前只会把默认值保存到浏览器 `localStorage`，不会持久化到服务端。

## 技术栈

### 后端
- **框架**：[FastAPI](https://fastapi.tiangolo.com/)
- **语言**：Python 3.11+
- **数据库**：[SQLite](https://www.sqlite.org/) + SQLAlchemy
- **迁移工具**：[Alembic](https://alembic.sqlalchemy.org/)
- **算法实现**：
  - 基于 NumPy 与 Haversine 距离的自定义约束 K-Means
  - 基于 NumPy 的自定义 GA-TSP 求解器
- **包管理器**：[uv](https://github.com/astral-sh/uv)

说明：仓库依赖中仍保留了 `scikit-learn`，但当前调度主流程没有直接调用 `sklearn.cluster.KMeans`。

### 前端
- **框架**：[Vue 3](https://vuejs.org/)（`<script setup>`）
- **语言**：TypeScript
- **UI 组件库**：[Element Plus](https://element-plus.org/)
- **地图**：[Leaflet](https://leafletjs.com/) + [Leaflet Ant Path](https://github.com/rubenspgcavalcante/leaflet-ant-path)
- **图表**：[ECharts](https://echarts.apache.org/)
- **状态管理**：[Pinia](https://pinia.vuejs.org/)
- **构建工具**：[Vite](https://vitejs.dev/)

## 安装与配置

### 前置要求
- Python 3.11+
- Node.js 18+
- 已安装 `uv`（`pip install uv`）

### 1. 后端设置

```bash
cd backend
uv sync
uv run alembic upgrade head
uv run python seed_shanghai_data.py
```

### 2. 前端设置

```bash
cd frontend
npm install
```

### Linux / 跨系统迁移说明

如果仓库是从 Windows 机器直接拷贝到 Linux，不要复用原有运行产物：

```bash
rm -f backend/sql_app.db backend/sql_app.db-shm backend/sql_app.db-wal
rm -rf frontend/node_modules
cd frontend && npm install
```

前端 npm 脚本通过 `node` 调用本地 CLI，不依赖源系统保留下来的可执行位。

### 一键启动

在仓库根目录执行：

```bash
# 重建数据库、执行迁移、初始化演示数据，并启动前后端
bash scripts/dev-up.sh

# 新机器首次启动
bash scripts/bootstrap-and-up.sh
```

可选环境变量：

```bash
BACKEND_HOST=0.0.0.0 BACKEND_PORT=8000 FRONTEND_HOST=0.0.0.0 FRONTEND_PORT=5173 bash scripts/dev-up.sh
```

## 运行应用

1. 启动后端：
   ```bash
   cd backend
   uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
2. 启动前端：
   ```bash
   cd frontend
   npm run dev
   ```
3. 打开 `http://localhost:5173`，登录后：
   - 进入 `AI调度中心`
   - 点击 `重置演示数据`
   - 点击 `开始AI调度`
   - 观察后台优化过程中地图路线的实时更新

## 仓库说明

- [backend/README.md](backend/README.md)：后端服务说明与算法入口
- [frontend/README.md](frontend/README.md)：前端应用说明与页面结构
- [docs/快递末端配送系统设计文档.md](docs/快递末端配送系统设计文档.md)：偏设计文档的项目说明

## 故障排除

### 数据库结构错误

如果遇到 `no such column` 或 `no such table`：

```bash
cd backend
rm -f sql_app.db sql_app.db-shm sql_app.db-wal
uv run alembic upgrade head
uv run python seed_shanghai_data.py
uv run uvicorn app.main:app --reload --port 8000
```

### Windows 上后端反复重启

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir app
```

---
*本项目是在 Claude Sonnet 4.5 的协助下开发的。*
