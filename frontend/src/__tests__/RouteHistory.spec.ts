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
    return () => h('button', { onClick: (event: MouseEvent) => emit('click', event) }, slots.default?.())
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

const DescriptionsItemStub = defineComponent({
  props: {
    label: String
  },
  setup(props, { slots }) {
    return () =>
      h('div', { class: 'el-descriptions-item' }, [
        props.label ? h('strong', props.label) : null,
        slots.default?.()
      ])
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
          'el-descriptions-item': DescriptionsItemStub,
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

  it('keeps only primary metrics in list cards and moves secondary metrics into the detail drawer', async () => {
    vi.mocked(axios.get).mockResolvedValueOnce({
      data: [
        {
          id: 11,
          title: '晨间调度',
          status: 'READY',
          created_at: '2026-04-04T08:00:00Z',
          algorithm_meta: { k: 3, generations: 180 },
          routes: [
            {
              id: 101,
              name: '路线1',
              geo_json: { total_distance_km: 12.4, package_count: 8, total_weight: 24.6 }
            },
            {
              id: 102,
              name: '路线2',
              geo_json: { total_distance_km: 9.6, package_count: 6, total_weight: 18.4 }
            }
          ]
        }
      ]
    })

    const wrapper = mount(RouteHistory, {
      global: {
        stubs: {
          'el-button': ButtonStub,
          'el-checkbox': genericStub('el-checkbox'),
          'el-checkbox-group': genericStub('el-checkbox-group'),
          'el-collapse': genericStub('el-collapse'),
          'el-collapse-item': genericStub('el-collapse-item'),
          'el-descriptions': genericStub('el-descriptions'),
          'el-descriptions-item': DescriptionsItemStub,
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

    expect(wrapper.text()).toContain('包裹数')
    expect(wrapper.text()).toContain('路线数')
    expect(wrapper.text()).toContain('总距离')
    expect(wrapper.text()).not.toContain('平均距离')
    expect(wrapper.text()).not.toContain('总重量')
    expect(wrapper.text()).not.toContain('K=3')

    const detailButton = wrapper.findAll('button').find((button) => button.text().includes('查看复盘'))
    await detailButton?.trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('总重量')
    expect(wrapper.text()).toContain('K值')
    expect(wrapper.text()).toContain('遗传代数')
  })
})
