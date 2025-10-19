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

app.mount('#app')


