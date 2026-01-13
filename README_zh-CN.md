# SmartDispatch-AI: 智能末端物流配送系统

[[English](README.md)]
> *基于 AI 的物流优化与现实约束处理*

**SmartDispatch-AI** 是一个全面的全栈解决方案，旨在解决“最后一公里”配送挑战。通过协同使用 **K-Means 聚类** 进行区域划分和 **遗传算法 (GA)** 进行路径优化，它能够生成尊重现实约束（如快递员运力）的高效配送计划。

该系统拥有用于高性能计算的 **FastAPI** 后端和用于沉浸式、数据丰富用户体验的 **Vue 3** 前端。

![系统截图](https://i.imgur.com/your-screenshot.png)

## 🚀 核心功能

### 🧠 智能核心
- **混合算法引擎**：结合 **约束 K-Means**（平衡聚类）与 **遗传算法**（TSP 求解器），最小化总行驶距离和成本。
- **动态运力管理**：根据实时包裹量和个人重量/体积限制（例如最大 150kg）自动调整快递员负载。
- **真实数据模拟**：集成 **上海** 真实地理数据，生成用于测试的逼真包裹地址和坐标。

### 🖥️ 交互式可视化
- **实时监控**：实时观看快递员沿优化路径移动，具有动态负载跟踪和交互式弹窗。
- **智能调度中心**：算法演进的可视化进度，展示路径如何代代优化。
- **蚂蚁路径动画**：Leaflet 地图上的动画路径可视化，清晰指示配送方向和流向。

### 📊 全面管理
- **一键调度**：单次点击触发复杂的优化任务。
- **数据分析**：富有洞察力的仪表板，显示快递员排名、效率趋势和成本节约指标。
- **生命周期跟踪**：全流程管理包裹状态：`待处理` (PENDING) -> `已分配` (ASSIGNED) -> `运输中` (IN_TRANSIT) -> `已送达` (DELIVERED)。
- **系统控制**：通过系统设置即时重置演示数据或清除历史记录。
    - **仪表板**：快速预览每日统计、效率趋势和快递员绩效。
    - **包裹管理**：跟踪包裹的整个生命周期（待处理、运输中、已送达）。
    - **快递员工作台**：监控快递员状态、工作量和绩效分析。
    - **分析与历史**：回顾过去的优化结果并分析绩效指标。
- **可配置**：直接从 UI 轻松调整算法参数（K 值、迭代代数）。

## 🛠️ 技术栈

### 后端 (Backend)
- **框架**：[FastAPI](https://fastapi.tiangolo.com/)
- **语言**：Python 3.11
- **数据库**：[SQLite](https://www.sqlite.org/) (简单起见，通过 SQLAlchemy)
- **迁移工具**：[Alembic](https://alembic.sqlalchemy.org/)
- **算法**：
    - [scikit-learn](https://scikit-learn.org/) 用于 K-Means 聚类。
    - 自定义构建的遗传算法（使用 NumPy）。
- **包管理器**：[uv](https://github.com/astral-sh/uv)

### 前端 (Frontend)
- **框架**：[Vue 3](https://vuejs.org/) (Composition API 搭配 `<script setup>`)
- **语言**：TypeScript
- **UI 工具包**：[Element Plus](https://element-plus.org/)
- **地图**：[Leaflet](https://leafletjs.com/) + [Leaflet Ant Path](https://github.com/rubenspgcavalcante/leaflet-ant-path)
- **图表**：[ECharts](https://echarts.apache.org/)
- **状态管理**：[Pinia](https://pinia.vuejs.org/)
- **构建工具**：[Vite](https://vitejs.dev/)
- **设计风格**：带有渐变背景的玻璃拟态 (Glassmorphism)

## ⚙️ 安装与配置

### 前置要求
- Python 3.10+
- Node.js 18+ 和 npm
- 已安装 `uv` (`pip install uv`)

### 1. 后端设置

```bash
# 进入后端目录
cd backend

# 安装依赖（自动创建虚拟环境）
uv sync

# 国内加速：
# uv sync --index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 应用数据库迁移
uv run alembic upgrade head

# 初始化数据库（配送站、快递员、包裹数据）
uv run python seed_shanghai_data.py
```

### 2. 前端设置

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install
```

## 🚀 运行应用程序

1.  **启动后端服务器**：
    ```bash
    cd backend
    uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ```
    API 将在 `http://localhost:8000` 上可用。

    > **注意**：在 Windows 上，如果服务器因 SQLite 文件变化而不断重启，请使用：
    > ```bash
    > uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir app
    > ```

2.  **启动前端服务器**：
    ```bash
    cd frontend
    npm run dev
    ```
    应用程序将在 `http://localhost:5173` 上可访问。

3.  **首次使用**：
    - 导航至 **AI调度中心**
    - 点击 **"🔄 重置演示数据"** 初始化随机包裹和快递员
    - 点击 **"🚀 开始AI调度"** 运行优化算法
    - 观看算法进行 K-Means 聚类和遗传算法优化的进度
    - 查看地图上带有动画路径的优化路线

## 🎨 设计特性

- **玻璃拟态 UI**：带有背景模糊效果的半透明卡片
- **渐变背景**：现代蓝紫色渐变主题
- **8 个核心页面**：仪表板、AI 调度中心、包裹流转、快递员工作台、实时监控、分析、路线历史、设置
- **动画路径可视化**：显示配送方向的蚂蚁路径动画
- **实时数据**：来自后端 API 的实时更新

---
*本项目是在 Claude Sonnet 4.5 的协助下开发的。*
