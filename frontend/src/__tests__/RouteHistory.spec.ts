import { defineComponent, h } from 'vue'
import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import axios from 'axios'

import RouteHistory from '../views/RouteHistory.vue'

vi.mock('axios')
vi.mock('echarts', () => ({
  init: vi.fn(() => ({
    setOption: vi.fn()
  }))
}))

const ButtonStub = defineComponent({
  emits: ['click'],
  setup(_, { emit, slots }) {
    return () => h('button', { onClick: () => emit('click') }, slots.default?.())
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

const genericStub = (className: string) =>
  defineComponent({
    setup(_, { slots }) {
      return () => h('div', { class: className }, slots.default?.())
    }
  })

describe('RouteHistory', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('shows an actionable empty state when there is no completed dispatch history yet', async () => {
    vi.mocked(axios.get).mockResolvedValueOnce({ data: [] })

    const wrapper = mount(RouteHistory, {
      global: {
        stubs: {
          'el-button': ButtonStub,
          'el-checkbox': genericStub('el-checkbox'),
          'el-checkbox-group': genericStub('el-checkbox-group'),
          'el-collapse': genericStub('el-collapse'),
          'el-collapse-item': genericStub('el-collapse-item'),
          'el-descriptions': genericStub('el-descriptions'),
          'el-descriptions-item': genericStub('el-descriptions-item'),
          'el-divider': genericStub('el-divider'),
          'el-drawer': genericStub('el-drawer'),
          'el-table': genericStub('el-table'),
          'el-table-column': genericStub('el-table-column'),
          'el-tag': genericStub('el-tag'),
          'router-link': RouterLinkStub
        }
      }
    })

    await flushPromises()

    expect(wrapper.text()).toContain('还没有已完成的调度记录')
    expect(wrapper.text()).toContain('先前往调度中心重置演示数据并发起一次调度')
    expect(wrapper.find('a[href="/dispatch"]').exists()).toBe(true)
  })
})
