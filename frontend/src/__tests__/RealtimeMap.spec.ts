import { defineComponent, h } from 'vue'
import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import L from 'leaflet'

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

const currentStation = {
  id: 6,
  name: '成都春熙路配送站',
  address: '成都市锦江区春熙路',
  latitude: 30.6586,
  longitude: 104.0817
}

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
    vi.mocked(axios.get)
      .mockResolvedValueOnce({ data: currentStation })
      .mockResolvedValueOnce({
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

  it('uses the latest route depot for the depot marker and replay center when it differs from the current station', async () => {
    vi.mocked(axios.get)
      .mockResolvedValueOnce({ data: currentStation })
      .mockResolvedValueOnce({
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
          }
        ]
      })

    mount(RealtimeMap, {
      global: {
        stubs: {
          'el-alert': AlertStub,
          'el-button': ButtonStub
        }
      }
    })

    await flushPromises()

    const mapInstance = vi.mocked(L.map).mock.results[0]?.value
    expect(mapInstance?.setView).toHaveBeenCalledWith([30.6586, 104.0817], 12)
    expect(mapInstance?.setView).toHaveBeenCalledWith([31.2304, 121.4737], 12)
    expect(vi.mocked(L.marker)).toHaveBeenCalledWith([31.2304, 121.4737], expect.anything())
  })

  it('keeps no-plan guidance in the page body instead of duplicating it with a toast', async () => {
    vi.mocked(axios.get)
      .mockResolvedValueOnce({ data: currentStation })
      .mockResolvedValueOnce({ data: [] })

    const wrapper = mount(RealtimeMap, {
      global: {
        stubs: {
          'el-alert': AlertStub,
          'el-button': ButtonStub
        }
      }
    })

    await flushPromises()

    expect(wrapper.text()).toContain('还没有可用于监控的调度计划')
    expect(vi.mocked(ElMessage.warning)).not.toHaveBeenCalled()
    expect(vi.mocked(ElMessage.error)).not.toHaveBeenCalled()
  })

  it('creates courier markers with explicit icon geometry for leaflet positioning', async () => {
    vi.mocked(axios.get)
      .mockResolvedValueOnce({ data: currentStation })
      .mockResolvedValueOnce({
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
          }
        ]
      })

    mount(RealtimeMap, {
      global: {
        stubs: {
          'el-alert': AlertStub,
          'el-button': ButtonStub
        }
      }
    })

    await flushPromises()

    const courierIconCall = vi
      .mocked(L.divIcon)
      .mock.calls.map(([options]) => options)
      .find((options) => options.className === 'custom-courier-icon')

    expect(courierIconCall).toEqual(
      expect.objectContaining({
        iconSize: [96, 32],
        iconAnchor: [48, 16]
      })
    )
  })

  it('creates numbered package markers with centered icon geometry', async () => {
    vi.mocked(axios.get)
      .mockResolvedValueOnce({ data: currentStation })
      .mockResolvedValueOnce({
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
                  package_count: 2,
                  coordinates: [
                    [121.4737, 31.2304],
                    [121.48, 31.24],
                    [121.49, 31.25],
                    [121.4737, 31.2304]
                  ],
                  packages_ordered: [
                    { recipient_name: 'A', tracking_number: 'T1', weight: 1 },
                    { recipient_name: 'B', tracking_number: 'T2', weight: 1 }
                  ]
                }
              }
            ]
          }
        ]
      })

    mount(RealtimeMap, {
      global: {
        stubs: {
          'el-alert': AlertStub,
          'el-button': ButtonStub
        }
      }
    })

    await flushPromises()

    const packageIconCall = vi
      .mocked(L.divIcon)
      .mock.calls.map(([options]) => options)
      .find((options) => typeof options.html === 'string' && options.html.includes('>1</div>'))

    expect(packageIconCall).toEqual(
      expect.objectContaining({
        iconSize: [24, 24],
        iconAnchor: [12, 12]
      })
    )
  })
})
