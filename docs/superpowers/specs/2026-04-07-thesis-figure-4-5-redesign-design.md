# Thesis Figure 4.5 Redesign Design

**Topic:** 图4.5 调度时序图重做

**Goal:** 基于项目真实代码链路，重做一张更适合论文阅读的调度时序图，减少拥挤、避免消息堆叠，并保留关键状态变化。

## 1. Real Flow Baseline

从当前代码看，真实调度链路为：

1. `SmartDispatch.vue` 发起 `POST /api/v1/dispatch/plans`
2. `dispatch.py` 校验站点并调用 `DispatchService.create_optimization_plan()`
3. API 通过 `BackgroundTasks.add_task(run_dispatch_background, plan_id)` 启动后台任务
4. `DispatchService.run_dispatch_algorithm(plan_id)` 读取站点、待分配包裹和可用快递员
5. 若无包裹或无快递员，计划直接置为 `COMPLETED`
6. 正常情况下执行 `ConstrainedKMeans`
7. 为每个 cluster 预创建 `DeliveryRoute`
8. 对每个 cluster 执行 `GeneticAlgorithmTSP`
9. GA 过程中周期性写入 `route.geo_json` 中间结果，状态经历 `calculating -> optimizing`
10. 全部优化完成后写入最终路线与包裹分配，`plan.status = READY`
11. 前端使用 `GET /api/v1/dispatch/plans/{id}` 轮询，直到拿到 `READY` 或 `COMPLETED` 后停止

## 2. Diagram Strategy

这张图不按“逐函数逐字段展开”绘制，而按“真实流程 + 论文可读性优先”重组。

保留真实职责，但合并过细参与者：

- `调度页面 SmartDispatch`
- `Dispatch API`
- `后台调度任务`
- `路径优化模块`
- `SQLite`

其中：

- `后台调度任务` 代表 `DispatchService + BackgroundTasks`
- `路径优化模块` 代表 `ConstrainedKMeans + GeneticAlgorithmTSP`

## 3. Sequence Structure

整张图拆成 5 个连续阶段：

### 阶段 A：创建计划

- `发起调度`
- `创建 plan`
- `返回 plan_id`
- `启动后台任务`

### 阶段 B：后台准备

- `读取待调度数据`
- `资源不足则结束`

说明：

- 不单独拆“校验站点”和“查询 station/packages/couriers”
- 这些细节合并到 API 创建计划与后台准备两个动作中

### 阶段 C：路径求解

- `执行聚类`
- `预建路线`
- `执行路径优化`
- `写中间进度`

说明：

- `执行路径优化` 表示对 cluster 逐个运行 GA
- `写中间进度` 表示周期性写入 `geo_json / generation / status`

### 阶段 D：前端轮询

- `轮询状态`
- `查询 plan/routes`
- `返回状态与路线`

说明：

- 这部分使用单独一个 `loop 轮询` 片段
- 不再把 `GET /plans/{id}` 完整接口写在主图中

### 阶段 E：完成收尾

- `写最终结果`
- `停止轮询`

说明：

- `写最终结果` 合并 route、package、plan 的最终写入
- `停止轮询` 用前端侧注释或虚线终止说明表示

## 4. Fragment Rules

只保留两个循环框和一个异常分支：

- `loop 轮询`
  - 包含前端、API、SQLite 三者之间的轮询查询与返回
- `loop 优化迭代`
  - 包含后台任务、路径优化模块、SQLite 三者之间的优化与进度写入
- `alt 资源不足`
  - 表达“无待调度包裹或无可用快递员时直接结束”

不再保留：

- `loop each cluster`
- `loop generation`

原因：

- 这两个 UML 片段叠在一起会明显挤压主图阅读空间
- 论文读者只需要知道“优化是迭代进行的”，不需要在时序图中看到双层嵌套循环

## 5. Layout Rules

### Main Area

- 主时序区控制在 `10` 到 `11` 条消息
- 参与者头框统一宽度
- 消息标签全部单行
- 每两条相邻消息垂直间距固定
- 激活条只保留 API、后台任务、SQLite 三处主激活，不给每条消息都加激活条

### Right Side

右侧不再保留两大块图例，只保留一个窄说明栏，内容控制为：

- `真实对应说明`
  - `发起调度 = POST /dispatch/plans`
  - `轮询状态 = GET /dispatch/plans/{id}`
  - `写中间进度 = 更新 route.geo_json`
  - `写最终结果 = 更新 route / package / plan`
- `状态`
  - `plan: OPTIMIZING -> READY / COMPLETED`
  - `route: calculating -> optimizing -> optimized`

## 6. Visual Direction

- 整体采用浅底、细线、蓝灰主线
- 组合框使用浅灰边框和低对比填充
- 说明栏弱化，不抢主图中心
- 图名独立放底部居中
- 不使用页面式卡片堆叠感，强调“论文章节配图”

## 7. Scope Check

这次重做只改：

- `frontend/src/views/ThesisFigure45.vue`

必要时同步改：

- `frontend/src/__tests__/ThesisFigure45.spec.ts`

不改动：

- 路由结构
- 其他论文图页面
- 后端实现逻辑

## 8. Acceptance Criteria

完成后的图应满足：

1. 主时序区一眼能区分 5 个参与者和 5 个阶段
2. 消息标签不重叠，不压在线和组合框上
3. 右侧说明栏明显比主图弱，不夺主视线
4. 轮询与优化两个循环都清楚，但不存在双层拥挤嵌套
5. 读者无需读右侧说明，也能看懂调度从创建到完成的闭环
