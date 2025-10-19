<template>
  <div v-if="tasks.length" class="mb-3 space-y-2">
    <div v-for="t in tasks" :key="t.id" class="flex items-center justify-between bg-base-700 rounded-lg px-3 py-2">
      <div class="text-sm text-accent-400 truncate">Downloading… ({{ t.id.slice(0,8) }})</div>
      <div class="text-xs text-accent-400">{{ t.state }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ tasks: { id: string; state: string }[] }>()
defineEmits(['refresh'])
</script>


