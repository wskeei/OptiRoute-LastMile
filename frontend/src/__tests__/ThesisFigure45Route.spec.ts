import { defineComponent, h } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

import App from '../App.vue'
import router from '../router'

const routeState = {
  path: '/thesis/figure-4-5',
  meta: {
    shell: false
  }
}

vi.mock('vue-router', async () => {
  const actual = await vi.importActual<typeof import('vue-router')>('vue-router')

  return {
    ...actual,
    useRoute: () => routeState
  }
})

const passthroughStub = (tag = 'div') =>
  defineComponent({
    setup(_, { slots }) {
      return () => h(tag, slots.default?.())
    }
  })

describe('thesis figure 4.5 route', () => {
  it('registers a public shell-less route', () => {
    const route = router.getRoutes().find((item) => item.path === '/thesis/figure-4-5')

    expect(route).toBeTruthy()
    expect(route?.meta.requiresAuth).toBe(false)
    expect(route?.meta.shell).toBe(false)
  })

  it('skips the application shell for thesis figure pages', () => {
    const wrapper = mount(App, {
      global: {
        stubs: {
          'router-view': passthroughStub()
        }
      }
    })

    expect(wrapper.find('.app-shell').exists()).toBe(false)
    expect(wrapper.find('.auth-layout').exists()).toBe(true)
  })
})
