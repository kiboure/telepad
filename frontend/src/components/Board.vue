<template>
  <div class="mt-4 rounded-xl bg-base-800 shadow-innerdeep p-4 relative">
    <div class="flex items-center gap-3 mb-4">
      <div v-if="mode==='library'" class="flex w-full items-center flex-wrap gap-x-2 gap-y-2">
        <div class="flex items-center flex-1 min-w-0">
          <input v-model="url" type="url" placeholder="Paste link to download"
                 class="min-w-0 flex-1 rounded-l-lg bg-base-700 px-3 py-2 outline-none focus:ring-1 focus:ring-accent-400" />
          <button @click="submitDownload" :disabled="!url || downloading"
                  class="shrink-0 rounded-r-lg bg-base-600 hover:bg-base-500 px-4 py-2">Download</button>
        </div>
        <button @click="triggerFilePicker" class="shrink-0 w-auto px-4 py-2 rounded-lg bg-base-700 hover:bg-base-600 text-accent-300">Upload</button>
        <input ref="fileInput" type="file" class="hidden" accept="audio/*,video/*" @change="onFilePicked" />
      </div>
      <div v-else class="flex w-full items-center flex-wrap gap-x-2 gap-y-2">
        <div class="flex items-center flex-1 min-w-0">
          <input v-model="search" @keyup.enter="doSearch()" placeholder="Search sounds" class="min-w-0 flex-1 rounded-l-lg bg-base-700 px-3 py-2 outline-none focus:ring-1 focus:ring-accent-400" />
          <button @click="doSearch()" class="shrink-0 rounded-r-lg bg-base-600 hover:bg-base-500 px-4 py-2">Search</button>
        </div>
        <button @click="openTagPicker" class="shrink-0 w-auto px-4 py-2 rounded-lg bg-base-700 hover:bg-base-600 text-accent-300">Filter</button>
      </div>
    </div>

    <div v-if="mode==='search'" class="mb-3">
      <div class="flex items-center gap-2 flex-wrap">
        <span v-for="t in selectedTags" :key="t" class="px-2 py-0.5 rounded-full bg-base-700 text-accent-300 text-xs">#{{ t }}</span>
        <button v-if="selectedTags.length" @click="clearTags" class="text-accent-400 text-xs">Clear</button>
      </div>
    </div>

    <div v-if="mode==='library'" class="mt-3">
      <TaskPlaceholders :tasks="tasks" @refresh="refresh" />
      <SoundList :mode="mode" :sounds="sounds" @refresh="refresh" />
      <div v-if="!sounds.length && !tasks.length" class="text-center text-accent-400 py-12">No saved sounds yet</div>
    </div>
    <div v-else>
      <SoundList :mode="mode" :sounds="sounds" @loadMore="loadMore" @refresh="refresh" />
      <div v-if="!sounds.length" class="text-center text-accent-400 py-12">No results</div>
    </div>
  </div>

  <div v-if="toastMessage" class="fixed inset-x-0 bottom-24 flex justify-center z-[60] pointer-events-none">
    <div class="pointer-events-auto bg-[#ca404dcc] text-accent-300 rounded-lg shadow-2xl px-4 py-2">
      {{ toastMessage }}
    </div>
  </div>
  <TagPicker :open="tagPickerOpen" :initialSelected="selectedTags" @apply="applyTags" @close="tagPickerOpen=false" />
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import axios from 'axios'
import SoundList from './SoundList.vue'
import TaskPlaceholders from './TaskPlaceholders.vue'
import TagPicker from './TagPicker.vue'

const props = defineProps<{ mode: 'library' | 'search' }>()

const url = ref('')
const search = ref('')
const sounds = ref<any[]>([])
const nextPage = ref<string | null>(null)
const downloading = ref(false)
const tasks = ref<{ id: string; state: string }[]>(JSON.parse(localStorage.getItem('dl_tasks') || '[]'))
const selectedTags = ref<string[]>([])
const tagPickerOpen = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)
const toastMessage = ref('')
let toastTimer: any = null

function triggerFilePicker() {
  fileInput.value?.click()
}

function showToast(msg: string, ms = 2500) {
  toastMessage.value = msg
  if (toastTimer) clearTimeout(toastTimer)
  toastTimer = setTimeout(() => (toastMessage.value = ''), ms)
}

async function onFilePicked(ev: Event) {
  const input = ev.target as HTMLInputElement
  if (!input.files || !input.files.length) return
  await handleFiles(input.files)
  input.value = ''
}

async function handleFiles(fileList: FileList) {
  const file = fileList[0]
  if (!file) return
  // Validate playable types
  const mime = (file.type || '').toLowerCase()
  const name = (file.name || '').toLowerCase()
  const playableMime = mime.startsWith('audio/') || mime.startsWith('video/')
  const allowedExt = [
    '.mp3','.wav','.ogg','.oga','.opus','.m4a','.aac','.flac','.alac','.wma','.amr',
    '.mp4','.m4v','.webm','.mkv','.mov','.avi'
  ]
  const hasAllowedExt = allowedExt.some(ext => name.endsWith(ext))
  if (!(playableMime || hasAllowedExt)) {
    showToast('Unsupported file type. Please choose an audio or video file.')
    return
  }
  const envMax = Number(import.meta.env.VITE_MAX_FILESIZE_MB)
  const maxMb = Number.isFinite(envMax) && envMax > 0 ? envMax : 20
  const sizeMb = file.size / 1024 / 1024
  if (sizeMb > maxMb) {
    showToast(`File exceeds the maximum size of ${maxMb}MB.`)
    return
  }
  try {
    const form = new FormData()
    form.append('file', file)
    const resp = await axios.post('/api/upload/', form, { headers: { 'Content-Type': 'multipart/form-data' } })
    const id = (resp.data as any)?.task_id
    if (id) {
      tasks.value.unshift({ id, state: 'PENDING' })
      localStorage.setItem('dl_tasks', JSON.stringify(tasks.value))
      pollTask(id)
    }
  } catch (err: any) {
    showToast('Upload failed')
  }
}

async function submitDownload() {
  if (!url.value) return
  downloading.value = true
  try {
    const resp = await axios.post('/api/download/', { url: url.value })
    const id = resp.data?.task_id
    if (id) {
      tasks.value.unshift({ id, state: 'PENDING' })
      localStorage.setItem('dl_tasks', JSON.stringify(tasks.value))
      pollTask(id)
    }
    url.value = ''
  } finally {
    downloading.value = false
  }
}

async function pollTask(id: string) {
  const timer = setInterval(async () => {
    try {
      const r = await axios.get(`/api/tasks/${id}/`)
      const st = r.data?.state
      const idx = tasks.value.findIndex(t => t.id === id)
      if (idx >= 0) tasks.value[idx].state = st
      if (st === 'SUCCESS' || st === 'FAILURE') {
        clearInterval(timer)
        if (st === 'SUCCESS') {
          const result = (r.data && (r.data as any).result) || null
          if (result && (result as any).status === 'Failed') {
            const detail = (result as any).detail as string | undefined
            showToast(formatTaskError(detail))
          } else {
            await refresh()
          }
        } else if (st === 'FAILURE') {
          const statusInfo = (r.data && (r.data as any).status) || 'Task failed'
          showToast(String(statusInfo))
        }
        tasks.value = tasks.value.filter(t => t.id !== id)
        localStorage.setItem('dl_tasks', JSON.stringify(tasks.value))
      }
    } catch {}
  }, 2000)
}

async function refresh() {
  if (props.mode === 'library') {
    const resp = await axios.get('/api/sounds/')
    sounds.value = resp.data?.results || []
    nextPage.value = resp.data?.next || null
  } else {
    await doSearch()
  }
}

function buildQuery(base: string) {
  const usp = new URLSearchParams()
  if (search.value) usp.set('search', search.value)
  selectedTags.value.forEach((t) => usp.append('tags', t))
  return `${base}?${usp.toString()}`
}

function normalizeUrl(u: string) {
  try { const a = new URL(u); return a.pathname + a.search } catch { return u }
}

async function doSearch(urlOverride?: string) {
  const endpoint = urlOverride ? normalizeUrl(urlOverride) : buildQuery('/api/sounds/all/')
  const resp = await axios.get(endpoint)
  sounds.value = resp.data?.results || []
  nextPage.value = resp.data?.next || null
}

async function loadMore() {
  if (!nextPage.value) return
  const resp = await axios.get(normalizeUrl(nextPage.value))
  sounds.value.push(...(resp.data?.results || []))
  nextPage.value = resp.data?.next || null
}

watch(() => props.mode, async (m) => {
  if (m === 'library') await refresh()
  else await doSearch()
})

onMounted(async () => {
  await refresh()
  // resume polling for existing pending tasks
  tasks.value.filter(t => !['SUCCESS','FAILURE'].includes(t.state)).forEach(t => pollTask(t.id))
})

function openTagPicker() { tagPickerOpen.value = true }
function applyTags(tags: string[]) { selectedTags.value = tags; doSearch() }
function clearTags() { selectedTags.value = []; doSearch() }

function formatTaskError(detail?: string): string {
  if (!detail) return 'Task failed'
  const m = detail.match(/Estimated file size exceeds\s+(\d+)MB\.?/i)
  if (m && m[1]) {
    return `File exceeds the maximum size of ${m[1]}MB.`
  }
  return detail
}
</script>


