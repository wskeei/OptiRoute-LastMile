import { defineComponent, h } from 'vue'
import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import axios from 'axios'

import RealtimeMap from '../views/RealtimeMap.vue'

vi.mock('axios')
vi.mock('leaflet', () => {
  const chainable = () => ({
    addTo: vi.fn().mockReturnThis(),
    bindPopup: vi.fn().mockReturnThis(),
    clearLayers: vi.fn(),
    setView: vi.fn().mockReturnThis(),
    invalidateSize: vi.fn(),
    setLatLng: vi.fn(),
    getPopup: vi.fn(() => null),
    setPopupContent: vi.fn()
  })

  return {
    default: {
      map: vi.fn(() => chainable()),
      tileLayer: vi.fn(() => ({ addTo: vi.fn() })),
      marker: vi.fn(() => chainable()),
      circle: vi.fn(() => chainable()),
      polyline: vi.fn(() => chainable()),
      divIcon: vi.fn()
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
        slots.default?.()
      ])
  }
})

describe('RealtimeMap', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('uses the newest completed result even when a READY plan also exists', async () => {
    vi.mocked(axios.get).mockResolvedValueOnce({
      data: [
        {
          id: 10,
          created_at: '2026-04-04T10:00:00Z',
          status: 'COMPLETED',
          routes: [
            {
              courier_id: 1,
              courier: { name: '完成计划快递员', max_capacity: 50 },
              geo_json: {
                color: '#184a68',
                package_count: 1,
                coordinates: [
                  [121.4737, 31.2304],
                  [121.48, 31.24],
                  [121.4737, 31.2304]
                ],
                packages_ordered: [{ recipient_name: 'A', tracking_number: 'T1', weight: 1 }]
              }
            }
          ]
        },
        {
          id: 9,
          created_at: '2026-04-03T10:00:00Z',
          status: 'READY',
          routes: [
            {
              courier_id: 2,
              courier: { name: '旧READY快递员', max_capacity: 50 },
              geo_json: {
                color: '#4c956c',
                package_count: 1,
                coordinates: [
                  [121.4737, 31.2304],
                  [121.49, 31.25],
                  [121.4737, 31.2304]
                ],
                packages_ordered: [{ recipient_name: 'B', tracking_number: 'T2', weight: 1 }]
              }
            }
          ]
        }
      ]
    })

    const wrapper = mount(RealtimeMap, {
      global: {
        stubs: {
          'el-alert': AlertStub,
          'el-button': ButtonStub
        }
      }
    })

    await flushPromises()

    expect(wrapper.text()).toContain('完成计划快递员')
    expect(wrapper.text()).not.toContain('旧READY快递员')
    expect(wrapper.text()).not.toContain('最近一次调度还没有可展示的路线结果')
  })
})
