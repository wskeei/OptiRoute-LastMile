import { defineComponent, h } from 'vue'
import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import axios from 'axios'

import SmartDispatch from '../views/SmartDispatch.vue'

vi.mock('axios')
vi.mock('leaflet', () => {
  const chainable = () => ({
    addTo: vi.fn().mockReturnThis(),
    bindPopup: vi.fn().mockReturnThis(),
    clearLayers: vi.fn(),
    setView: vi.fn().mockReturnThis(),
    invalidateSize: vi.fn()
  })

  return {
    default: {
      map: vi.fn(() => chainable()),
      tileLayer: vi.fn(() => ({ addTo: vi.fn() })),
      marker: vi.fn(() => chainable()),
      circleMarker: vi.fn(() => chainable()),
      circle: vi.fn(() => chainable()),
      layerGroup: vi.fn(() => chainable()),
      divIcon: vi.fn(),
      polyline: { antPath: vi.fn(() => ({ addTo: vi.fn() })) }
    }
  }
})
vi.mock('leaflet-ant-path', () => ({}))
vi.mock('element-plus', () => ({
  ElMessage: {
    success: vi.fn(),
    info: vi.fn(),
    warning: vi.fn(),
    error: vi.fn()
  }
}))

const ButtonStub = defineComponent({
  props: {
    disabled: Boolean,
    loading: Boolean,
    type: String
  },
  emits: ['click'],
  setup(props, { emit, slots }) {
    return () =>
      h(
        'button',
        {
          class: ['el-button', props.type ? `el-button--${props.type}` : ''],
          disabled: props.disabled,
          'data-loading': String(props.loading),
          onClick: () => emit('click')
        },
        slots.default?.()
      )
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

const FormStub = defineComponent({
  setup(_, { slots }) {
    return () => h('form', { class: 'el-form' }, slots.default?.())
  }
})

const FormItemStub = defineComponent({
  setup(_, { slots }) {
    return () => h('div', { class: 'el-form-item' }, slots.default?.())
  }
})

const StepsStub = defineComponent({
  setup(_, { slots }) {
    return () => h('div', { class: 'el-steps' }, slots.default?.())
  }
})

const StepStub = defineComponent({
  setup(_, { slots }) {
    return () => h('div', { class: 'el-step' }, slots.default?.())
  }
})

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

const mountComponent = () =>
  mount(SmartDispatch, {
    global: {
      stubs: {
        'el-alert': AlertStub,
        'el-button': ButtonStub,
        'el-form': FormStub,
        'el-form-item': FormItemStub,
        'el-step': StepStub,
        'el-steps': StepsStub,
        'router-link': RouterLinkStub
      }
    }
  })

describe('SmartDispatch', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('explains the demo-only dispatch controls to the user', async () => {
    vi.mocked(axios.get)
      .mockResolvedValueOnce({ data: [{ status: 'PENDING', latitude: 31.2, longitude: 121.4 }] })
      .mockResolvedValueOnce({ data: [{ status: 'AVAILABLE' }] })
      .mockResolvedValueOnce({ data: [] })

    const wrapper = mountComponent()
    await flushPromises()

    expect(wrapper.text()).toContain('这个页面只保留会影响当前体验的真实动作')
    expect(wrapper.text()).toContain('聚类数会根据当前可用快递员数量自动确定')
    expect(wrapper.text()).toContain('遗传算法迭代次数和种群规模使用后端固定配置')
  })

  it('keeps the dispatch action disabled when the sample data is not ready', async () => {
    vi.mocked(axios.get)
      .mockResolvedValueOnce({ data: [{ status: 'ASSIGNED', latitude: 31.2, longitude: 121.4 }] })
      .mockResolvedValueOnce({ data: [{ status: 'OFF_DUTY' }] })
      .mockResolvedValueOnce({ data: [] })

    const wrapper = mountComponent()
    await flushPromises()

    const dispatchButton = wrapper.findAll('button').find((button) => button.text().includes('开始调度'))
    expect(dispatchButton?.attributes('disabled')).toBeDefined()
  })

  it('creates a dispatch plan without sending fake frontend tuning parameters', async () => {
    vi.mocked(axios.get)
      .mockResolvedValueOnce({ data: [{ status: 'PENDING', latitude: 31.2, longitude: 121.4 }] })
      .mockResolvedValueOnce({ data: [{ status: 'AVAILABLE' }] })
      .mockResolvedValueOnce({ data: [] })
    vi.mocked(axios.post).mockResolvedValueOnce({ data: { id: 9 } })

    const wrapper = mountComponent()
    await flushPromises()

    const dispatchButton = wrapper.findAll('button').find((button) => button.text().includes('开始调度'))
    await dispatchButton?.trigger('click')

    expect(axios.post).toHaveBeenCalledWith(
      '/api/v1/dispatch/plans',
      expect.objectContaining({
        station_id: 1
      })
    )
    expect(vi.mocked(axios.post).mock.calls[0]?.[1]).not.toHaveProperty('algorithm_meta')
  })

  it('keeps polling failures visible in the page body with recovery guidance', async () => {
    vi.useFakeTimers()

    vi.mocked(axios.get)
      .mockResolvedValueOnce({ data: [{ status: 'PENDING', latitude: 31.2, longitude: 121.4 }] })
      .mockResolvedValueOnce({ data: [{ status: 'AVAILABLE' }] })
      .mockResolvedValueOnce({ data: [] })
      .mockRejectedValueOnce(new Error('poll failed'))
    vi.mocked(axios.post).mockResolvedValueOnce({ data: { id: 9 } })

    const wrapper = mountComponent()
    await flushPromises()

    const dispatchButton = wrapper.findAll('button').find((button) => button.text().includes('开始调度'))
    await dispatchButton?.trigger('click')
    await flushPromises()

    await vi.advanceTimersByTimeAsync(1000)
    await flushPromises()

    expect(wrapper.text()).toContain('调度状态获取失败')
    expect(wrapper.text()).toContain('可以重新发起调度，或先点击“重置演示数据”刷新样本')
  })
})
