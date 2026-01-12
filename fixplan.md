K-Means + 遗传算法多车配送路径规划系统 - 实施计划
核心目标: 让算法规划结果在地图上清晰可视化，修复所有非功能性UI元素

Phase 1: 核心算法可视化 (最高优先级)
1.1 完善地图路径显示
[MODIFY] 

SmartDispatch.vue
当前问题: 路径只显示简单折线，无法区分不同快递员的路线

修改内容:

为每条路线使用不同颜色（5条路线 = 5种颜色）
添加路径动画（蚂蚁线效果）展示配送方向
显示聚类区域边界（K-Means结果可视化）
添加起点/终点标记（配送站图标）
包裹点显示顺序编号
+ import 'leaflet-ant-path'  // 添加蚂蚁线动画
+ const ROUTE_COLORS = ['#667eea', '#48bb78', '#ed8936', '#f56565', '#9f7aea']
+ // 绘制聚类区域多边形
+ // 为每条路线添加动画效果
[MODIFY] 

dispatch_service.py
当前问题: geo_json 只存储坐标，缺少路径元数据

修改内容:

返回每条路线的总距离（km）
返回每条路线的包裹数量
返回优化前后的距离对比
添加聚类中心坐标
route.geo_json = {
    "type": "LineString",
    "coordinates": [...],
+   "cluster_center": [lat, lon],
+   "total_distance_km": 12.5,
+   "package_count": 8,
+   "color": "#667eea"
}
1.2 生成真实上海地点数据
[NEW] 

seed_shanghai_data.py
功能: 使用LLM生成的真实上海地点替换随机坐标

内容:

100个真实上海地址（小区、商场、写字楼）
对应的经纬度坐标
合理的收件人信息
Phase 2: 后端API补全
2.1 统计数据API
[NEW] 

stats.py
@router.get("/dashboard")
def get_dashboard_stats():
    """返回Dashboard需要的统计数据"""
    return {
        "pending_count": 127,
        "in_transit_count": 85,
        "completed_count": 342,
        "online_couriers": 5,
        "efficiency_improvement": 12.5
    }
@router.get("/courier-ranking")
def get_courier_ranking():
    """返回快递员排行榜"""
2.2 历史记录API
[MODIFY] 

dispatch.py
新增端点:

@router.get("/plans")
def list_dispatch_plans():
    """获取所有调度计划历史"""
@router.get("/plans/{plan_id}/routes")
def get_plan_routes():
    """获取某个计划的所有路线详情"""
Phase 3: 前端功能修复
3.1 Dashboard页面
[MODIFY] 

Dashboard.vue
修复项	说明
统计数字	调用 /api/v1/stats/dashboard 获取真实数据
快递员排行	调用 /api/v1/stats/courier-ranking
效率趋势图	调用历史数据API
3.2 包裹管理页面
[MODIFY] 

PackageFlow.vue
修复项	说明
表格数据	调用 /api/v1/delivery/packages
搜索功能	实现前端过滤或后端搜索
扫码入库按钮	弹出对话框输入快递单号
导出按钮	导出CSV功能
状态筛选	连接后端筛选API
3.3 快递员工作台
[MODIFY] 

CourierWork.vue
修复项	说明
快递员列表	调用 /api/v1/delivery/couriers
添加快递员按钮	弹出表单对话框
状态切换	可操作的状态下拉框
3.4 其他页面
页面	修复内容
RealtimeMap.vue	显示当前所有快递员位置（模拟）
DeliveryAnalytics.vue	连接统计API，图表展示真实数据
RouteHistory.vue	调用历史计划API，显示过往调度
SystemSettings.vue	算法参数可保存，配送站可编辑
Phase 4: UI细节打磨
4.1 全局交互改进
 所有按钮添加 loading 状态
 表格添加空状态提示
 添加操作成功/失败 Toast 提示
 对话框统一样式
4.2 地图组件优化
 添加地图图例（颜色说明）
 路线hover显示详情tooltip
 包裹点点击显示收件人信息
 添加全屏模式
4.3 响应式适配
 侧边栏折叠时布局调整
验证计划
自动化测试
cd backend && pytest tests/algorithms/  # 验证算法正确性
手动验证
执行 seed-data 填充测试数据
在 SmartDispatch 页面点击"开始智能调度"
验证地图显示5条不同颜色的配送路线
检查所有页面按钮可点击
优先级排序
优先级	任务	预估时间
P0	SmartDispatch 路径可视化完善	2h
P0	上海真实地点数据	1h
P1	Dashboard API对接	1h
P1	PackageFlow 功能修复	1.5h
P2	CourierWork 功能修复	1h
P2	其他页面API对接	2h
P3	UI细节打磨	2h
总预估时间: 10-12小时

已确认决策
✅ LLM生成100个真实上海地址
❌ 不需要移动端App设计
❌ 不需要实时监控WebSocket