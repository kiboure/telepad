<template>
  <div class="mt-4 rounded-xl bg-base-800 shadow-innerdeep p-4">
    <div class="flex items-center gap-3 mb-4">
      <div v-if="mode==='library'" class="flex w-full">
        <input v-model="url" type="url" placeholder="Paste link to download"
               class="flex-1 rounded-l-lg bg-base-700 px-3 py-2 outline-none focus:ring-1 focus:ring-accent-400" />
        <button @click="submitDownload" :disabled="!url || downloading"
                class="rounded-r-lg bg-base-600 hover:bg-base-500 px-4">Download</button>
      </div>
      <div v-else class="flex w-full">
        <input v-model="search" placeholder="Search sounds" class="flex-1 rounded-l-lg bg-base-700 px-3 py-2 outline-none focus:ring-1 focus:ring-accent-400" />
        <button @click="doSearch" class="rounded-r-lg bg-base-600 hover:bg-base-500 px-4">Search</button>
      </div>
    </div>

    <div v-if="mode==='library'">
      <TaskPlaceholders :tasks="tasks" @refresh="refresh" />
      <SoundList :mode="mode" :sounds="sounds" @refresh="refresh" />
      <div v-if="!sounds.length && !tasks.length" class="text-center text-accent-400 py-12">No saved sounds yet</div>
    </div>
    <div v-else>
      <SoundList :mode="mode" :sounds="sounds" @loadMore="loadMore" @refresh="refresh" />
      <div v-if="!sounds.length" class="text-center text-accent-400 py-12">No results</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import axios from 'axios'
import SoundList from './SoundList.vue'
import TaskPlaceholders from './TaskPlaceholders.vue'

const props = defineProps<{ mode: 'library' | 'search' }>()

const url = ref('')
const search = ref('')
const sounds = ref<any[]>([])
const nextPage = ref<string | null>(null)
const downloading = ref(false)
const tasks = ref<{ id: string; state: string }[]>(JSON.parse(localStorage.getItem('dl_tasks') || '[]'))

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
        if (st === 'SUCCESS') await refresh()
        tasks.value = tasks.value.filter(t => !(t.id === id && st === 'SUCCESS'))
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

async function doSearch(urlOverride?: string) {
  const endpoint = urlOverride || `/api/sounds/all/?search=${encodeURIComponent(search.value)}`
  const resp = await axios.get(endpoint)
  sounds.value = resp.data?.results || []
  nextPage.value = resp.data?.next || null
}

async function loadMore() {
  if (!nextPage.value) return
  const resp = await axios.get(nextPage.value)
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
</script>


