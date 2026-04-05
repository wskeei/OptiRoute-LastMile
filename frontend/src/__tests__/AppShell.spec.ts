import { defineComponent, h } from 'vue'
import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import App from '../App.vue'

const routeState = { path: '/dispatch' }

vi.mock('vue-router', () => ({
  useRoute: () => routeState
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

const passthroughStub = (tag = 'div') =>
  defineComponent({
    setup(_, { slots }) {
      return () => h(tag, slots.default?.())
    }
  })

const mountApp = (width = 900) => {
  Object.defineProperty(window, 'innerWidth', {
    configurable: true,
    writable: true,
    value: width
  })

  return mount(App, {
    global: {
      stubs: {
        'el-icon': passthroughStub(),
        'router-link': RouterLinkStub,
        'router-view': passthroughStub()
      }
    }
  })
}

describe('App shell', () => {
  beforeEach(() => {
    routeState.path = '/dispatch'
  })

  it('keeps the core routes visible in compact navigation', () => {
    const wrapper = mountApp()
    const primaryNav = wrapper.get('[aria-label="主要导航"]')

    expect(primaryNav.find('a[href="/dispatch"]').exists()).toBe(true)
    expect(primaryNav.find('a[href="/monitor"]').exists()).toBe(true)
    expect(primaryNav.find('a[href="/history"]').exists()).toBe(true)
    expect(primaryNav.find('a[href="/dashboard"]').exists()).toBe(true)
  })

  it('does not render the removed shell summary copy', () => {
    const wrapper = mountApp()

    expect(wrapper.text()).not.toContain('先重置数据，再启动调度，然后查看路线结果。')
    expect(wrapper.text()).not.toContain('主要操作保留在上方，分析和系统页面收纳在“更多页面”。')
  })

  it('does not show the environment badge text in the sidebar brand area', () => {
    const wrapper = mountApp(1280)

    expect(wrapper.text()).not.toContain('演示环境')
  })

  it('shows the shorter product title in the sidebar brand area', () => {
    const wrapper = mountApp(1280)

    expect(wrapper.text()).toContain('配送调度系统')
    expect(wrapper.text()).not.toContain('末端配送调度系统')
  })

  it('adds a real collapsed layout state on desktop when the sidebar toggle is pressed', async () => {
    const wrapper = mountApp(1280)

    await wrapper.get('button.sidebar-toggle').trigger('click')

    expect(wrapper.get('.app-shell').classes()).toContain('shell-collapsed')
    expect(wrapper.get('.sidebar').classes()).toContain('collapsed')
  })
})
