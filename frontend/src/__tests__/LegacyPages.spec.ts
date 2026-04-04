import { defineComponent, h } from 'vue'
import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import axios from 'axios'

import CourierWork from '../views/CourierWork.vue'
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

const DialogStub = defineComponent({
  props: {
    width: {
      type: String,
      default: ''
    },
    title: {
      type: String,
      default: ''
    }
  },
  setup(props, { slots }) {
    return () =>
      h('div', { class: 'el-dialog', 'data-width': props.width, 'data-title': props.title }, [
        slots.default?.(),
        slots.footer?.()
      ])
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

    vi.mocked(axios.get).mockResolvedValueOnce({ data: [] })

    const wrapper = mount(CourierWork, {
      global: {
        stubs: {
          'el-avatar': passthroughStub('el-avatar'),
          'el-button': ButtonStub,
          'el-dialog': DialogStub,
          'el-form': passthroughStub('el-form'),
          'el-form-item': passthroughStub('el-form-item'),
          'el-input': passthroughStub('el-input'),
          'el-input-number': passthroughStub('el-input-number'),
          'el-tag': passthroughStub('el-tag')
        }
      }
    })

    await flushPromises()

    expect(wrapper.get('.el-dialog').attributes('data-width')).toBe('90vw')
  })

  it('keeps settings explanations collapsed until the user asks for details', async () => {
    vi.mocked(axios.get)
      .mockResolvedValueOnce({ data: [{ id: 1 }, { id: 2 }] })
      .mockResolvedValueOnce({ data: [{ id: 1 }] })
      .mockResolvedValueOnce({ data: [{ id: 1 }] })

    const wrapper = mount(Settings, {
      global: {
        stubs: {
          'el-button': ButtonStub
        }
      }
    })

    await flushPromises()

    expect(wrapper.text()).toContain('展开说明')
    expect(wrapper.text()).not.toContain('聚类数会根据当前可用快递员数量自动确定')
    expect(wrapper.text()).not.toContain('当前系统展示的是演示流程，不是生产调度后台')
  })
})
