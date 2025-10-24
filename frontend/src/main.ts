import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import './styles.css'
import axios from 'axios'
import { useAuth } from './stores/auth'


const app = createApp(App)
const pinia = createPinia()
app.use(pinia)
try { const auth = useAuth(pinia); auth.init() } catch {}

axios.interceptors.request.use((config) => {
  try {
    const u = typeof config.url === 'string' ? new URL(config.url, window.location.origin) : null
    if (u && u.protocol === 'http:') {
      u.protocol = 'https:'
      config.url = u.toString()
    }
  } catch {}
  return config
})

try {
  const params = new URLSearchParams(window.location.search)
  const id = params.get('id')
  if (id) {
    const username = params.get('username') || ''
    const auth = useAuth(pinia)
    auth.login({ telegram_id: Number(id), username })
    const url = new URL(window.location.href)
    url.search = ''
    window.history.replaceState({}, '', url.toString())
  }
} catch {}

window.addEventListener('tg-auth', (e: any) => {
  try {
    const auth = useAuth(pinia)
    const data = e.detail || {}
    const payload: any = {}
    ;['id','username','first_name','last_name','photo_url','auth_date','hash'].forEach((k) => {
      if (data[k] !== undefined && data[k] !== null && data[k] !== '') payload[k] = data[k]
    })
    if (payload.id) payload.id = Number(payload.id)
    if (payload.auth_date) payload.auth_date = Number(payload.auth_date)
    auth.login(payload)
  } catch {}
})

app.mount('#app')


