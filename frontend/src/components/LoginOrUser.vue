<template>
  <div>
    <div v-if="isAuthed" class="flex items-center gap-3">
      <img v-if="user?.photo_url" :src="user.photo_url" class="w-8 h-8 rounded-full object-cover" alt="pfp" />
      <div class="text-sm">{{ user?.username || ('id ' + user?.telegram_id) }}</div>
      <button @click="logout" class="text-accent-400 hover:text-accent-300 text-sm">Logout</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuth } from '../stores/auth'

const auth = useAuth()
const isAuthed = auth.isAuthenticated
const user = auth.user

onMounted(() => {
  window.addEventListener('tg-auth', (e: any) => {
    const data = e.detail
    // For now, send telegram_id and username only (hash later)
    auth.login({ telegram_id: Number(data.id), username: data.username || '' })
  })
})

async function logout() {
  await auth.logout()
}
</script>


