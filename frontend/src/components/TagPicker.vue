<template>
  <div v-if="open" class="fixed inset-0 z-50 grid place-items-center bg-black/50" @click.self="close">
    <div class="w-[min(92vw,380px)] rounded-xl bg-base-800 p-5 shadow-2xl">
      <div class="mb-4 text-accent-300 text-lg flex items-center justify-between">
        <span>Tags</span>
        <span class="text-accent-400 text-sm">{{ selectedCount }}/10</span>
      </div>
      <div class="flex gap-2 mb-4">
        <input v-model="query" @keyup.enter="resetAndSearch" placeholder="Add or create tags..." class="flex-1 bg-base-700 rounded-lg px-4 py-3 outline-none focus:ring-1 focus:ring-accent-400 text-base" />
        <button @click="resetAndSearch" class="px-4 py-3 rounded-lg bg-base-600 hover:bg-base-500 text-base">Search</button>
      </div>
      <div ref="scrollBox" class="min-h-28 max-h-80 overflow-auto pr-1 space-y-1">
        <div v-if="!loading && results.length===0" class="h-40 flex flex-col items-center justify-center gap-2">
          <div class="text-accent-300 opacity-40 text-sm">No tags found</div>
          <button @click="createTag" :disabled="limitReached" class="text-accent-300 opacity-70 hover:opacity-100 underline disabled:opacity-30 disabled:cursor-not-allowed">Create tag</button>
        </div>
        <div v-for="t in results" :key="t" class="flex items-center justify-between bg-base-700 rounded-lg px-3 py-2">
          <div class="text-accent-300 text-base">#{{ t }}</div>
          <input type="checkbox" class="scale-110" :checked="selectedSet.has(t)" :disabled="!selectedSet.has(t) && limitReached" @change="toggle(t)" />
        </div>
      </div>
      <div v-if="limitReached" class="mt-2 text-accent-400 text-xs">You reached the 10 tags limit.</div>
      <div class="mt-5 flex justify-end gap-3">
        <button @click="apply" class="px-4 py-2 rounded-lg bg-base-600 hover:bg-base-500 text-base">Add</button>
        <button @click="close" class="px-4 py-2 rounded-lg bg-base-600 hover:bg-base-500 text-base">Cancel</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, computed } from 'vue'
import axios from 'axios'

const props = defineProps<{ open: boolean; initialSelected: string[] }>()
const emit = defineEmits(['close','apply'])

const query = ref('')
const loading = ref(false)
const results = ref<string[]>([])
const selectedSet = ref<Set<string>>(new Set(props.initialSelected || []))
const nextUrl = ref<string | null>(null)
const scrollBox = ref<HTMLElement | null>(null)
const MAX_TAGS = 10
const selectedCount = computed(() => selectedSet.value.size)
const limitReached = computed(() => selectedCount.value >= MAX_TAGS)

watch(() => props.initialSelected, (v) => { selectedSet.value = new Set(v || []) })
watch(() => props.open, (o) => { if (o) resetAndSearch() })

function normalize(u: string) { try { const a = new URL(u); return a.pathname + a.search } catch { return u } }

async function search(append = false) {
  loading.value = true
  try {
    const base = '/api/tags/'
    const url = append && nextUrl.value ? normalize(nextUrl.value) : `${base}?search=${encodeURIComponent(query.value)}`
    const resp = await axios.get(url)
    const page = (resp.data?.results || []).map((x: any) => x.name)
    results.value = append ? results.value.concat(page) : page
    nextUrl.value = resp.data?.next || null
  } finally { loading.value = false }
}

function resetAndSearch() { nextUrl.value = null; results.value = []; search(false) }

function toggle(t: string) {
  const s = selectedSet.value
  if (s.has(t)) s.delete(t)
  else {
    if (s.size >= MAX_TAGS) return
    s.add(t)
  }
}

function createTag() {
  const name = query.value.trim()
  if (!name) return
  if (!results.value.includes(name)) results.value.unshift(name)
  const s = selectedSet.value
  if (s.has(name)) { query.value = ''; return }
  if (s.size >= MAX_TAGS) return
  s.add(name)
  query.value = ''
}

function apply() {
  emit('apply', Array.from(selectedSet.value))
  close()
}

function close() { emit('close') }

onMounted(() => {
  const el = scrollBox.value
  if (!el) return
  el.addEventListener('scroll', () => {
    if (!nextUrl.value || loading.value) return
    if (el.scrollTop + el.clientHeight >= el.scrollHeight - 20) {
      search(true)
    }
  })
})
</script>


