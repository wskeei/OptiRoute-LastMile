import { defineComponent, h } from 'vue'
import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import axios from 'axios'

import Analytics from '../views/Analytics.vue'
import Dashboard from '../views/Dashboard.vue'

vi.mock('axios')
vi.mock('echarts', () => ({
  init: vi.fn(() => ({
    setOption: vi.fn()
  }))
}))

const RouterLinkStub = defineComponent({
  props: {
    to: {
      type: String,
      required: true
    }
  },
  setup(props, { slots }) {
    return () => h('a', { href: props.to }, slots.default?.())
  }
})

const ButtonStub = defineComponent({
  emits: ['click'],
  setup(_, { emit, slots }) {
    return () => h('button', { onClick: () => emit('click') }, slots.default?.())
  }
})

const AlertStub = defineComponent({
  props: {
    title: String
  },
  setup(props, { slots }) {
    return () =>
      h('div', { class: 'el-alert' }, [
        props.title ? h('strong', props.title) : null,
        slots.title?.(),
        slots.default?.()
      ])
  }
})

const mountWithStubs = (component: any) =>
  mount(component, {
    global: {
      stubs: {
        'el-alert': AlertStub,
        'el-button': ButtonStub,
        'router-link': RouterLinkStub
      }
    }
  })

describe('page-level persistent feedback', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('shows an inline dashboard error state when the overview data fails to load', async () => {
    vi.mocked(axios.get).mockRejectedValueOnce(new Error('network failed'))

    const wrapper = mountWithStubs(Dashboard)
    await flushPromises()

    expect(wrapper.text()).toContain('任务概览加载失败')
    expect(wrapper.text()).toContain('请刷新页面或前往调度中心重新开始')
  })

  it('shows an inline analytics error state when the analysis data fails to load', async () => {
    vi.mocked(axios.get).mockRejectedValueOnce(new Error('network failed'))

    const wrapper = mountWithStubs(Analytics)
    await flushPromises()

    expect(wrapper.text()).toContain('运营分析加载失败')
    expect(wrapper.text()).toContain('请稍后重试，或先前往调度中心生成一条新的调度结果')
  })
})
