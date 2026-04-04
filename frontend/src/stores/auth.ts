import { defineStore } from 'pinia'
import axios from 'axios'

interface User {
  id: number
  username: string
  full_name: string | null
  role: string
  is_active: boolean
}

interface AuthState {
  token: string | null
  user: User | null
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    token: localStorage.getItem('token') || null,
    user: null
  }),

  getters: {
    isAuthenticated: (state) => !!state.token
  },

  actions: {
    async login(username: string, password: string) {
      try {
        const response = await axios.post('/api/v1/auth/login', { username, password })
        this.token = response.data.access_token
        localStorage.setItem('token', this.token!)
        await this.fetchUser()
        return true
      } catch (error: any) {
        console.error('Login failed:', error)
        throw error
      }
    },

    async register(username: string, password: string, fullName: string) {
      try {
        await axios.post('/api/v1/auth/register', {
          username,
          password,
          full_name: fullName
        })
        // 注册成功后自动登录
        await this.login(username, password)
        return true
      } catch (error: any) {
        console.error('Registration failed:', error)
        throw error
      }
    },

    async fetchUser() {
      if (!this.token) return
      try {
        const response = await axios.get('/api/v1/auth/me', {
          headers: { Authorization: `Bearer ${this.token}` }
        })
        this.user = response.data
      } catch (error) {
        console.error('Failed to fetch user:', error)
        this.logout()
      }
    },

    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('token')
    }
  }
})
