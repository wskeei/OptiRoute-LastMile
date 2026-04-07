import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import ThesisFigure45 from '../views/ThesisFigure45.vue'

describe('ThesisFigure45', () => {
  it('renders the required sequence participants, fragments, legend, and caption', () => {
    const wrapper = mount(ThesisFigure45)
    const text = wrapper.text()

    expect(text).toContain('调度页面 SmartDispatch')
    expect(text).toContain('Dispatch API')
    expect(text).toContain('后台调度任务')
    expect(text).toContain('路径优化模块')
    expect(text).toContain('SQLite')

    expect(text).toContain('发起调度')
    expect(text).toContain('创建 plan')
    expect(text).toContain('返回 plan_id')
    expect(text).toContain('启动后台任务')
    expect(text).toContain('读取待调度数据')
    expect(text).toContain('执行聚类')
    expect(text).toContain('预建路线')
    expect(text).toContain('执行路径优化')
    expect(text).toContain('写中间进度')
    expect(text).toContain('轮询状态')
    expect(text).toContain('查询 plan/routes')
    expect(text).toContain('返回状态与路线')
    expect(text).toContain('写最终结果')
    expect(text).toContain('停止轮询')

    expect(text).toContain('loop 轮询')
    expect(text).toContain('loop 优化迭代')
    expect(text).toContain('alt 资源不足')
    expect(text).toContain('真实对应说明')
    expect(text).toContain('状态')
    expect(text).toContain('OPTIMIZING')
    expect(text).toContain('READY / COMPLETED')
    expect(text).not.toContain('无待调度包裹或无可用快递员时，后台任务直接写结束状态')
    expect(text).not.toContain('聚类后逐步优化路线，并持续把中间进度写回 SQLite')
    expect(text).not.toContain('前端每秒轮询一次，直到拿到 READY / COMPLETED')
    expect(text).not.toContain('loop each cluster')
    expect(text).not.toContain('loop generation')
    expect(text).toContain('图4.5 调度时序图')
  })
})
