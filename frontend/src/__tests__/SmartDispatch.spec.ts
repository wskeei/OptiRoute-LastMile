/**
 * SmartDispatch Component Tests
 *
 * To run these tests, install testing dependencies:
 * npm install -D vitest @vue/test-utils happy-dom
 *
 * Then add to package.json scripts:
 * "test": "vitest"
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import SmartDispatch from '../views/SmartDispatch.vue'
import axios from 'axios'

vi.mock('axios')
vi.mock('leaflet', () => ({
  default: {
    map: vi.fn(() => ({
      setView: vi.fn(() => ({ addTo: vi.fn() })),
      eachLayer: vi.fn(),
      removeLayer: vi.fn()
    })),
    tileLayer: vi.fn(() => ({ addTo: vi.fn() })),
    marker: vi.fn(() => ({ addTo: vi.fn(() => ({ bindPopup: vi.fn() })) })),
    divIcon: vi.fn(),
    circle: vi.fn(() => ({ addTo: vi.fn() }))
  }
}))

describe('SmartDispatch Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should render the component', () => {
    const wrapper = mount(SmartDispatch)
    expect(wrapper.find('h2').text()).toBe('🤖 AI智能调度中心')
  })

  it('should display reset and dispatch buttons', () => {
    const wrapper = mount(SmartDispatch)
    const buttons = wrapper.findAll('button')
    expect(buttons.length).toBeGreaterThanOrEqual(2)
  })

  it('should fetch package and courier data on mount', async () => {
    const mockPackages = [
      { id: 1, tracking_number: 'TEST001', status: 'PENDING' }
    ]
    const mockCouriers = [
      { id: 1, name: '测试快递员', status: 'AVAILABLE' }
    ]

    vi.mocked(axios.get).mockResolvedValueOnce({ data: mockPackages })
    vi.mocked(axios.get).mockResolvedValueOnce({ data: mockCouriers })

    const wrapper = mount(SmartDispatch)
    await wrapper.vm.$nextTick()

    expect(axios.get).toHaveBeenCalledWith('/api/v1/delivery/packages?status=PENDING')
    expect(axios.get).toHaveBeenCalledWith('/api/v1/delivery/couriers')
  })

  it('should call reset API when reset button is clicked', async () => {
    vi.mocked(axios.post).mockResolvedValueOnce({ data: { message: 'success' } })
    vi.mocked(axios.get).mockResolvedValue({ data: [] })

    const wrapper = mount(SmartDispatch)
    await wrapper.vm.$nextTick()

    const resetButton = wrapper.find('button[type="warning"]')
    await resetButton.trigger('click')

    expect(axios.post).toHaveBeenCalledWith('/api/v1/dispatch/reset-demo')
  })

  it('should start dispatch when dispatch button is clicked', async () => {
    const mockPlan = { id: 1, title: '测试计划', status: 'PENDING' }
    vi.mocked(axios.post).mockResolvedValueOnce({ data: mockPlan })
    vi.mocked(axios.get).mockResolvedValue({ data: [] })

    const wrapper = mount(SmartDispatch)
    await wrapper.vm.$nextTick()

    const dispatchButton = wrapper.find('button[type="primary"]')
    await dispatchButton.trigger('click')

    expect(axios.post).toHaveBeenCalledWith(
      '/api/v1/dispatch/plans',
      expect.objectContaining({
        station_id: 1,
        algorithm_meta: expect.any(Object)
      })
    )
  })

  it('should display progress steps during dispatch', async () => {
    const wrapper = mount(SmartDispatch)

    // Simulate loading state
    await wrapper.setData({ loading: true, step: 2 })

    const steps = wrapper.findAll('.el-step')
    expect(steps.length).toBe(4)
  })

  it('should display result after successful dispatch', async () => {
    const wrapper = mount(SmartDispatch)

    await wrapper.setData({
      result: { savedDistance: 25.3, savedCost: 156 }
    })

    const alert = wrapper.find('.el-alert')
    expect(alert.exists()).toBe(true)
    expect(alert.text()).toContain('25.3')
  })
})
