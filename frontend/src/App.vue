<template>
  <div class="min-h-full flex flex-col">
    <header v-if="isAuthed" class="px-5 py-4 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="text-2xl font-semibold tracking-wide font-mono">Telepad</div>
        <div class="text-sm text-accent-400 font-mono">@tlpadbot</div>
      </div>
      <LoginOrUser />
    </header>
    <main class="flex-1 px-4 pb-6">
      <div class="max-w-3xl mx-auto">
        <template v-if="isAuthed">
          <Toggle v-model="mode" />
          <Board :mode="mode" />
          <div class="fixed inset-x-0 bottom-6 flex justify-center pointer-events-none">
            <div class="pointer-events-auto group relative flex items-center gap-2 bg-base-700/80 backdrop-blur rounded-xl shadow-2xl px-3 py-2 text-accent-300 cursor-pointer"
                 @mouseenter="showHelp = true" @mouseleave="showHelp = false" @click="showHelp = !showHelp" tabindex="0" role="button" aria-label="How to use sounds help">
              <div class="w-5 h-5 rounded-full bg-base-600 grid place-items-center text-accent-300">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
              </div>
              <div class="text-base">How to use sounds?</div>
              <div v-show="showHelp" class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 z-50 bg-base-800 rounded-lg shadow-2xl px-3 py-2 text-sm text-accent-300 whitespace-pre-line w-[min(90vw,520px)]">
                To use your created or saved sounds, open any chat in Telegram and type @tlpadbot. Your sounds will appear above the keyboard.
              </div>
            </div>
          </div>
        </template>
        <template v-else>
          <div class="h-[70vh] grid place-items-center">
            <div class="flex flex-col items-center gap-6 w-full">
              <div class="font-bold font-mono text-[10vw] leading-tight max-w-[50vw] text-center">Telepad</div>
              <div class="text-accent-400 text-sm">The Telegram-integrated soundboard.</div>
              <TelegramLogin />
            </div>
          </div>
        </template>
      </div>
    </main>
  </div>
  
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import Toggle from './components/Toggle.vue'
import Board from './components/Board.vue'
import LoginOrUser from './components/LoginOrUser.vue'
import TelegramLogin from './components/TelegramLogin.vue'
import { useAuth } from './stores/auth'

const mode = ref<'library' | 'search'>('library')
const auth = useAuth()
const isAuthed = computed(() => auth.isAuthenticated)
const showHelp = ref(false)

function updateBodyClass() {
  if (isAuthed.value) {
    document.body.classList.add('auth')
    document.body.classList.remove('unauth')
  } else {
    document.body.classList.add('unauth')
    document.body.classList.remove('auth')
  }
}

onMounted(updateBodyClass)
watch(isAuthed, updateBodyClass)
</script>


