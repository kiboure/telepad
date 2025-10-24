<template>
  <div>
    <div v-if="isAuthed" ref="wrapper" class="relative">
      <button @click="toggleMenu" class="font-mono text-sm cursor-pointer hover:opacity-80 transition-opacity" aria-haspopup="true" aria-expanded="showMenu ? 'true' : 'false'">
        {{ user?.username || ('id ' + user?.telegram_id) }}
      </button>
      <div v-if="showMenu" class="absolute right-0 mt-2 w-56 rounded-lg shadow-2xl bg-base-800/95 backdrop-blur text-accent-300 z-50">
        <div v-if="user?.first_name" class="px-4 py-2 truncate">{{ user?.first_name }}</div>
        <div class="px-4 py-2 truncate">{{ user?.telegram_id }}</div>
        <div class="h-px bg-base-700/60 my-1"></div>
        <button @click="onLogout" class="w-full text-left px-4 py-2 text-sm" :style="{ color: '#ca404dcc' }">Logout</button>
      </div>
    </div>
  </div>
  
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useAuth } from '../stores/auth'

const auth = useAuth()
const isAuthed = auth.isAuthenticated
const user = auth.user

const showMenu = ref(false)
const wrapper = ref<HTMLElement | null>(null)


function toggleMenu() {
  showMenu.value = !showMenu.value
}

async function onLogout() {
  showMenu.value = false
  await auth.logout()
}

function handleClickOutside(ev: MouseEvent) {
  if (!showMenu.value) return
  const el = wrapper.value
  if (el && !el.contains(ev.target as Node)) {
    showMenu.value = false
  }
}

onMounted(() => {
  window.addEventListener('click', handleClickOutside)
})
onBeforeUnmount(() => {
  window.removeEventListener('click', handleClickOutside)
})
</script>


