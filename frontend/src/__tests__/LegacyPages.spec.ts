import { defineComponent, h } from 'vue'
import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import axios from 'axios'

import CourierWork from '../views/CourierWork.vue'
import PackageFlow from '../views/PackageFlow.vue'
import Settings from '../views/Settings.vue'

vi.mock('axios')
vi.mock('element-plus', () => ({
  ElMessage: {
    success: vi.fn(),
    error: vi.fn(),
    info: vi.fn()
  },
  ElMessageBox: {
    confirm: vi.fn()
  }
}))

const ButtonStub = defineComponent({
  emits: ['click'],
  setup(_, { emit, slots }) {
    return () => h('button', { onClick: (event: MouseEvent) => emit('click', event) }, slots.default?.())
  }
})

const InputStub = defineComponent({
  props: {
    modelValue: {
      type: [String, Number],
      default: ''
    },
    placeholder: {
      type: String,
      default: ''
    }
  },
  emits: ['update:modelValue'],
  setup(props, { emit, slots }) {
    return () =>
      h('div', { class: 'el-input' }, [
        slots.prefix?.(),
        h('input', {
          value: props.modelValue,
          placeholder: props.placeholder,
          onInput: (event: Event) => emit('update:modelValue', (event.target as HTMLInputElement).value)
        })
      ])
  }
})

const InputNumberStub = defineComponent({
  props: {
    modelValue: {
      type: Number,
      default: 0
    }
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    return () =>
      h('input', {
        class: 'el-input-number',
        type: 'number',
        value: props.modelValue,
        onInput: (event: Event) =>
          emit('update:modelValue', Number((event.target as HTMLInputElement).value))
      })
  }
})

const SelectStub = defineComponent({
  props: {
    modelValue: {
      type: String,
      default: ''
    }
  },
  emits: ['update:modelValue'],
  setup(props, { emit, slots }) {
    return () =>
      h(
        'select',
        {
          class: 'el-select',
          value: props.modelValue,
          onChange: (event: Event) => emit('update:modelValue', (event.target as HTMLSelectElement).value)
        },
        slots.default?.()
      )
  }
})

const OptionStub = defineComponent({
  props: {
    label: {
      type: String,
      default: ''
    },
    value: {
      type: String,
      default: ''
    }
  },
  setup(props) {
    return () => h('option', { value: props.value }, props.label)
  }
})

const DialogStub = defineComponent({
  props: {
    modelValue: {
      type: Boolean,
      default: true
    },
    width: {
      type: String,
      default: ''
    },
    title: {
      type: String,
      default: ''
    }
  },
  emits: ['update:modelValue'],
  setup(props, { slots }) {
    return () =>
      h('div', { class: 'el-dialog', 'data-width': props.width, 'data-title': props.title }, [
        slots.default?.(),
        slots.footer?.()
      ])
  }
})

const TableStub = defineComponent({
  setup(_, { slots }) {
    return () => h('div', { class: 'el-table' }, slots.default?.())
  }
})

const TableColumnStub = defineComponent({
  props: {
    label: {
      type: String,
      default: ''
    }
  },
  setup(props, { slots }) {
    return () =>
      h(
        'div',
        { class: 'el-table-column', 'data-label': props.label },
        slots.default?.({ row: { status: 'PENDING' } })
      )
  }
})

const passthroughStub = (className: string) =>
  defineComponent({
    setup(_, { slots }) {
      return () => h('div', { class: className }, slots.default?.())
    }
  })

describe('legacy page follow-up fixes', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('uses a mobile-safe dialog width for adding couriers', async () => {
    Object.defineProperty(window, 'innerWidth', {
      configurable: true,
      writable: true,
      value: 375
    })

    vi.mocked(axios.get).mockImplementation(async (url) => {
      if (url === '/api/v1/delivery/stations/current') {
        return { data: { id: 3, name: '杭州钱江新城配送站' } }
      }
      return { data: [] }
    })

    const wrapper = mount(CourierWork, {
      global: {
        stubs: {
          'el-avatar': passthroughStub('el-avatar'),
          'el-button': ButtonStub,
          'el-dialog': DialogStub,
          'el-form': passthroughStub('el-form'),
          'el-form-item': passthroughStub('el-form-item'),
          'el-input': InputStub,
          'el-input-number': InputNumberStub,
          'el-tag': passthroughStub('el-tag')
        }
      }
    })

    await flushPromises()

    expect(wrapper.get('.el-dialog').attributes('data-width')).toBe('90vw')
  })

  it('removes the settings explanation section entirely', async () => {
    vi.mocked(axios.get).mockImplementation(async (url) => {
      if (url === '/api/v1/delivery/stations/current') {
        return {
          data: {
            id: 1,
            name: '上海人民广场配送站',
            address: '上海市黄浦区人民广场',
            latitude: 31.2304,
            longitude: 121.4737
          }
        }
      }
      if (url === '/api/v1/delivery/packages') {
        return { data: [{ id: 1 }, { id: 2 }] }
      }
      return { data: [{ id: 1 }] }
    })

    const wrapper = mount(Settings, {
      global: {
        stubs: {
          'el-button': ButtonStub,
          'el-form': passthroughStub('el-form'),
          'el-form-item': passthroughStub('el-form-item'),
          'el-input': InputStub,
          'el-input-number': InputNumberStub
        }
      }
    })

    await flushPromises()

    expect(wrapper.text()).not.toContain('运行与演示边界')
    expect(wrapper.text()).not.toContain('展开说明')
    expect(wrapper.text()).not.toContain('聚类数会根据当前可用快递员数量自动确定')
  })

  it('renders a main-station form and saves edits through the current-station endpoint', async () => {
    vi.mocked(axios.get).mockImplementation(async (url) => {
      if (url === '/api/v1/delivery/stations/current') {
        return {
          data: {
            id: 1,
            name: '上海人民广场配送站',
            address: '上海市黄浦区人民广场',
            latitude: 31.2304,
            longitude: 121.4737
          }
        }
      }
      if (url === '/api/v1/delivery/packages') {
        return { data: [{ id: 1 }, { id: 2 }] }
      }
      return { data: [{ id: 1 }] }
    })
    vi.mocked(axios.patch).mockResolvedValueOnce({ data: { id: 1 } })

    const wrapper = mount(Settings, {
      global: {
        stubs: {
          'el-button': ButtonStub,
          'el-form': passthroughStub('el-form'),
          'el-form-item': passthroughStub('el-form-item'),
          'el-input': InputStub,
          'el-input-number': InputNumberStub
        }
      }
    })

    await flushPromises()

    const inputs = wrapper.findAll('input')
    await inputs[0]?.setValue('杭州钱江新城配送站')
    await inputs[1]?.setValue('杭州市上城区钱江新城')
    await inputs[2]?.setValue('30.2459')
    await inputs[3]?.setValue('120.2108')

    const saveButton = wrapper.findAll('button').find((button) => button.text().includes('保存主配送站'))
    await saveButton?.trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('主配送站')
    expect(axios.patch).toHaveBeenCalledWith('/api/v1/delivery/stations/current', {
      name: '杭州钱江新城配送站',
      address: '杭州市上城区钱江新城',
      latitude: 30.2459,
      longitude: 120.2108
    })
  })

  it('posts a random-city reset payload from settings', async () => {
    vi.mocked(axios.get).mockImplementation(async (url) => {
      if (url === '/api/v1/delivery/stations/current') {
        return {
          data: {
            id: 6,
            name: '成都春熙路配送站',
            address: '成都市锦江区春熙路',
            latitude: 30.6586,
            longitude: 104.0817
          }
        }
      }
      if (url === '/api/v1/delivery/packages') {
        return { data: [{ id: 1 }, { id: 2 }] }
      }
      return { data: [{ id: 1 }] }
    })
    vi.mocked(axios.post).mockResolvedValueOnce({ data: { message: 'ok' } })

    const wrapper = mount(Settings, {
      global: {
        stubs: {
          'el-button': ButtonStub,
          'el-form': passthroughStub('el-form'),
          'el-form-item': passthroughStub('el-form-item'),
          'el-input': InputStub,
          'el-input-number': InputNumberStub
        }
      }
    })

    await flushPromises()

    const randomResetButton = wrapper.findAll('button').find((button) => button.text().includes('随机城市重置'))
    await randomResetButton?.trigger('click')
    await flushPromises()

    expect(axios.post).toHaveBeenCalledWith('/api/v1/dispatch/reset-demo', { randomize_station: true })
  })

  it('submits package coordinates around the current main station', async () => {
    const randomSpy = vi.spyOn(Math, 'random').mockReturnValue(0.5)

    vi.mocked(axios.get).mockImplementation(async (url) => {
      if (url === '/api/v1/delivery/stations/current') {
        return {
          data: {
            id: 6,
            name: '成都春熙路配送站',
            address: '成都市锦江区春熙路',
            latitude: 30.6586,
            longitude: 104.0817
          }
        }
      }
      return { data: [] }
    })
    vi.mocked(axios.post).mockResolvedValueOnce({ data: { id: 1 } })

    const wrapper = mount(PackageFlow, {
      global: {
        stubs: {
          'el-button': ButtonStub,
          'el-dialog': DialogStub,
          'el-form': passthroughStub('el-form'),
          'el-form-item': passthroughStub('el-form-item'),
          'el-input': InputStub,
          'el-input-number': InputNumberStub,
          'el-select': SelectStub,
          'el-option': OptionStub,
          'el-table': TableStub,
          'el-table-column': TableColumnStub,
          'el-tag': passthroughStub('el-tag'),
          'el-row': passthroughStub('el-row'),
          'el-col': passthroughStub('el-col'),
          'el-icon': passthroughStub('el-icon')
        }
      }
    })

    await flushPromises()

    const submitButton = wrapper.findAll('button').find((button) => button.text().includes('入库'))
    await submitButton?.trigger('click')
    await flushPromises()

    expect(axios.post).toHaveBeenCalledWith(
      '/api/v1/delivery/packages',
      expect.objectContaining({
        latitude: 30.6586,
        longitude: 104.0817
      })
    )

    randomSpy.mockRestore()
  })

  it('uses the current main station id when creating a courier', async () => {
    vi.mocked(axios.get).mockImplementation(async (url) => {
      if (url === '/api/v1/delivery/stations/current') {
        return { data: { id: 6, name: '成都春熙路配送站' } }
      }
      return { data: [] }
    })
    vi.mocked(axios.post).mockResolvedValueOnce({ data: { id: 1 } })

    const wrapper = mount(CourierWork, {
      global: {
        stubs: {
          'el-avatar': passthroughStub('el-avatar'),
          'el-button': ButtonStub,
          'el-dialog': DialogStub,
          'el-form': passthroughStub('el-form'),
          'el-form-item': passthroughStub('el-form-item'),
          'el-input': InputStub,
          'el-input-number': InputNumberStub,
          'el-tag': passthroughStub('el-tag')
        }
      }
    })

    await flushPromises()

    const confirmButton = wrapper.findAll('button').find((button) => button.text().includes('确定'))
    await confirmButton?.trigger('click')
    await flushPromises()

    expect(axios.post).toHaveBeenCalledWith(
      '/api/v1/delivery/couriers',
      expect.objectContaining({ station_id: 6 })
    )
  })
})
