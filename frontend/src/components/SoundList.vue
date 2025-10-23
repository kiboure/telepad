<template>
  <div class="space-y-2 max-h-[70vh] overflow-auto pr-1">
    <div v-for="s in sounds" :key="s.id" class="flex items-center gap-3 bg-base-700 rounded-xl px-3 py-2">
      <button @click="togglePlay(s)" class="w-8 h-8 rounded-full bg-base-600 hover:bg-base-500 grid place-items-center">
        <span v-if="current?.id===s.id && playing">❚❚</span>
        <span v-else>▶</span>
      </button>
      <div class="flex-1 min-w-0">
        <div v-if="editingId!==s.id" class="truncate">{{ s.name }}</div>
        <input v-else v-model="editName" class="w-full bg-base-600 rounded-lg px-2 py-1" />
        <div class="mt-1 flex flex-wrap gap-1">
          <template v-if="editingId!==s.id">
            <span v-for="t in (s.tags||[])" :key="t" class="px-2 py-0.5 rounded-full bg-base-600 text-accent-300 text-sm">#{{ t }}</span>
          </template>
          <template v-else>
            <button @click="openTags(s)" class="px-2 py-0.5 rounded-md bg-base-600 text-accent-300 text-sm">Edit Tags</button>
            <span v-for="t in (pendingTags)" :key="t" class="px-2 py-0.5 rounded-full bg-base-600 text-accent-300 text-sm">#{{ t }}</span>
          </template>
        </div>
        <div class="text-xs text-accent-400">{{ durationLabel(s) }}</div>
      </div>
      <div class="flex items-center gap-2">
        <template v-if="mode==='library' && editingId!==s.id">
          <template v-if="s.owner === currentUserId">
            <button @click="startEdit(s)" class="text-accent-300 hover:text-accent-200" title="Edit">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 1 1 3 3L7 19l-4 1 1-4 12.5-12.5z"/></svg>
            </button>
            <button @click="hideUnhide(s)" class="text-accent-300 hover:text-accent-200" :title="s.is_private? 'Make public' : 'Make private'">
              <svg v-if="s.is_private" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
            </button>
          </template>
          <button @click="confirmUnsave(s)" class="text-danger hover:opacity-90" title="Remove from Library">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M6 2h12a2 2 0 0 1 2 2v18l-8-4-8 4V4a2 2 0 0 1 2-2z"/></svg>
          </button>
        </template>
        <template v-else-if="mode==='search'">
          <button @click="saveUnsave(s)" class="text-accent-300 hover:text-accent-200" :title="s.is_saved? 'Unsave' : 'Save'">
            <svg v-if="!s.is_saved" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21l-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M6 2h12a2 2 0 0 1 2 2v18l-8-4-8 4V4a2 2 0 0 1 2-2z"/></svg>
          </button>
          <div class="flex items-center gap-1 ml-2 text-accent-300" title="Like">
            <button @click="likeUnlike(s)" class="text-accent-300 hover:text-accent-200">
              <svg v-if="!s.is_liked" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78L12 21.23l8.84-8.84a5.5 5.5 0 0 0 0-7.78z"/></svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 6 4 4 6.5 4c1.74 0 3.41 1.01 4.22 2.44C11.09 5.01 12.76 4 14.5 4 17 4 19 6 19 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>
            </button>
            <span class="text-xs">{{ s.likes_count || 0 }}</span>
          </div>
        </template>
        <template v-else>
          <button @click="applyEdit(s)" class="text-sm text-success">Apply</button>
          <button @click="cancelEdit" class="text-sm text-accent-400">Cancel</button>
        </template>
      </div>
    </div>
    <div v-if="mode==='search' && hasMore" class="py-3 text-center">
      <button @click="$emit('loadMore')" class="px-4 py-2 rounded-lg bg-base-600 hover:bg-base-500">Load more</button>
    </div>
  </div>
  <TagPicker :open="tagPickerOpen" :initialSelected="pendingTags" @apply="applyTags" @close="tagPickerOpen=false" />
  <ConfirmModal :open="confirmOpen" :message="confirmMsg" @confirm="() => { confirmOpen=false; if (confirmAction) confirmAction() }" @cancel="() => { confirmOpen=false; confirmAction=null }" />
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import axios from 'axios'
import TagPicker from './TagPicker.vue'
import ConfirmModal from './ConfirmModal.vue'
import { useAuth } from '../stores/auth'

const props = defineProps<{ sounds: any[]; mode: 'library' | 'search'; hasMore?: boolean }>()
const emit = defineEmits(['refresh', 'loadMore'])

const audio = new Audio()
const current = ref<any | null>(null)
const playing = ref(false)
audio.onended = () => { playing.value = false }

function urlFor(s: any) {
  return s.file_path?.startsWith('http') ? s.file_path : `/media/${s.file_path}`
}

function togglePlay(s: any) {
  if (current.value?.id === s.id && playing.value) {
    audio.pause(); playing.value = false; return
  }
  audio.src = urlFor(s)
  audio.play()
  current.value = s
  playing.value = true
}

function durationLabel(s: any) {
  const d = s.duration || 0
  const m = Math.floor(d / 60)
  const sec = (d % 60).toString().padStart(2, '0')
  return `${m}:${sec}`
}

const editingId = ref<number | null>(null)
const editName = ref('')
const pendingTags = ref<string[]>([])
const tagPickerOpen = ref(false)
const confirmOpen = ref(false)
const confirmMsg = ref('')
let confirmAction: null | (() => Promise<void> | void) = null

// Current user for ownership checks
const auth = useAuth()
const currentUserId = computed(() => auth.user?.id)

function startEdit(s: any) {
  editingId.value = s.id
  editName.value = s.name
  pendingTags.value = [...(s.tags || [])]
}
function cancelEdit() {
  editingId.value = null
  editName.value = ''
  pendingTags.value = []
}
async function applyEdit(s: any) {
  await axios.patch(`/api/sounds/${s.id}/`, { name: editName.value, tags: pendingTags.value })
  editingId.value = null
  await emit('refresh')
}

async function likeUnlike(s: any) {
  const path = s.is_liked ? 'unlike' : 'like'
  await axios.post(`/api/sounds/${s.id}/${path}/`)
  await emit('refresh')
}

function confirmUnsave(s: any) {
  confirmMsg.value = 'Remove this sound?'
  confirmAction = async () => {
    await axios.post(`/api/sounds/${s.id}/unsave/`)
    await emit('refresh')
  }
  confirmOpen.value = true
}

async function saveUnsave(s: any) {
  const path = s.is_saved ? 'unsave' : 'save'
  if (path === 'unsave') {
    confirmMsg.value = 'Remove this sound?'
    confirmAction = async () => {
      await axios.post(`/api/sounds/${s.id}/${path}/`)
      await emit('refresh')
    }
    confirmOpen.value = true
    return
  }
  await axios.post(`/api/sounds/${s.id}/${path}/`)
  await emit('refresh')
}

function openTags(s: any) { tagPickerOpen.value = true }
function applyTags(newTags: string[]) { pendingTags.value = newTags }

function openConfirm(message: string, action: () => Promise<void> | void) {
  confirmMsg.value = message
  confirmAction = action
  confirmOpen.value = true
}

async function hideUnhide(s: any) {
  if (s.is_private) {
    openConfirm('Make your sound public? Users who save the sound will still have it even if you hide it again.', async () => {
      await axios.post(`/api/sounds/${s.id}/unhide/`)
      await emit('refresh')
    })
  } else {
    openConfirm('Make your sound private?', async () => {
      await axios.post(`/api/sounds/${s.id}/hide/`)
      await emit('refresh')
    })
  }
}
</script>

<style scoped>
</style>


