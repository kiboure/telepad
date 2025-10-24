import { defineStore } from 'pinia'
import axios from 'axios'

type TGLogin = { telegram_id: number; username?: string }

export const useAuth = defineStore('auth', {
  state: () => ({
    user: null as null | { id: number; telegram_id: number; username?: string; first_name?: string },
    access: null as string | null,
    refresh: null as string | null,
    loading: false,
  }),
  getters: {
    isAuthenticated: (s) => !!s.user,
  },
  actions: {
    init() {
      try {
        const savedUser = localStorage.getItem('tp_user')
        const savedAccess = localStorage.getItem('tp_access')
        const savedRefresh = localStorage.getItem('tp_refresh')
        this.user = savedUser ? JSON.parse(savedUser) : null
        this.access = savedAccess || null
        this.refresh = savedRefresh || null
        if (this.access) axios.defaults.headers.common['Authorization'] = `Bearer ${this.access}`
      } catch {}
    },
    async login(payload: TGLogin) {
      this.loading = true
      try {
        const resp = await axios.post('/api/login/', payload)
        this.user = resp.data?.user
        this.access = resp.data?.access
        this.refresh = resp.data?.refresh
        if (this.access) axios.defaults.headers.common['Authorization'] = `Bearer ${this.access}`
        localStorage.setItem('tp_user', JSON.stringify(this.user))
        if (this.access) localStorage.setItem('tp_access', this.access)
        if (this.refresh) localStorage.setItem('tp_refresh', this.refresh)
        window.dispatchEvent(new Event('tp-auth-changed'))
      } finally {
        this.loading = false
      }
    },
    async logout() {
      try { await axios.post('/api/logout/') } catch {}
      this.user = null; this.access = null; this.refresh = null
      delete axios.defaults.headers.common['Authorization']
      localStorage.removeItem('tp_user')
      localStorage.removeItem('tp_access')
      localStorage.removeItem('tp_refresh')
      window.dispatchEvent(new Event('tp-auth-changed'))
    },
    async refreshToken() {
      if (!this.refresh) return
      const resp = await axios.post('/api/token/refresh/', { refresh: this.refresh })
      this.access = resp.data?.access
      if (this.access) axios.defaults.headers.common['Authorization'] = `Bearer ${this.access}`
      if (this.access) localStorage.setItem('tp_access', this.access)
    }
  },
})


