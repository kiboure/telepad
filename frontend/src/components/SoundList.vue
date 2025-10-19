<template>
  <div class="space-y-2 max-h-[70vh] overflow-auto pr-1">
    <div v-for="s in sounds" :key="s.id" class="flex items-center gap-3 bg-base-700 rounded-xl px-3 py-2">
      <button @click="togglePlay(s)" class="w-8 h-8 rounded-full bg-base-600 hover:bg-base-500 grid place-items-center">
        <span v-if="current?.id===s.id && playing">❚❚</span>
        <span v-else>▶</span>
      </button>
      <div class="flex-1 min-w-0">
        <div v-if="editingId!==s.id" class="truncate">{{ s.name }}</div>
        <input v-else v-model="editName" class="w-full bg-base-600 rounded px-2 py-1" />
        <div class="text-xs text-accent-400">
          <span>{{ durationLabel(s) }}</span>
          <span v-if="s.tags?.length"> • {{ s.tags.join(', ') }}</span>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <template v-if="mode==='library' && editingId!==s.id">
          <button @click="startEdit(s)" class="text-sm text-accent-400 hover:text-accent-300">Edit</button>
          <button @click="likeUnlike(s)" class="text-sm text-accent-400 hover:text-accent-300">{{ s.is_liked? 'Unlike' : 'Like' }}</button>
          <button @click="unsave(s)" class="text-sm text-danger hover:opacity-90">Remove</button>
        </template>
        <template v-else-if="mode==='search'">
          <button @click="saveUnsave(s)" class="text-sm text-accent-400 hover:text-accent-300">{{ s.is_saved? 'Remove' : 'Save' }}</button>
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
</template>

<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'

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

function startEdit(s: any) {
  editingId.value = s.id
  editName.value = s.name
}
function cancelEdit() {
  editingId.value = null
  editName.value = ''
}
async function applyEdit(s: any) {
  await axios.patch(`/api/sounds/${s.id}/`, { name: editName.value })
  editingId.value = null
  await emit('refresh')
}

async function likeUnlike(s: any) {
  const path = s.is_liked ? 'unlike' : 'like'
  await axios.post(`/api/sounds/${s.id}/${path}/`)
  await emit('refresh')
}

async function unsave(s: any) {
  await axios.post(`/api/sounds/${s.id}/unsave/`)
  await emit('refresh')
}

async function saveUnsave(s: any) {
  const path = s.is_saved ? 'unsave' : 'save'
  await axios.post(`/api/sounds/${s.id}/${path}/`)
  await emit('refresh')
}
</script>


