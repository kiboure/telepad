<template>
  <div v-if="open" class="fixed inset-0 z-50 grid place-items-center bg-black/50" @click.self="$emit('cancel')">
    <div class="w-[min(92vw,480px)] rounded-lg bg-base-800 p-4 shadow-2xl">
      <div class="text-accent-300 mb-3">{{ message }}</div>
      <div class="flex justify-end gap-2">
        <button @click="$emit('confirm')" class="px-3 py-1 rounded-lg bg-base-600 hover:bg-base-500">Confirm</button>
        <button @click="$emit('cancel')" class="px-3 py-1 rounded-lg bg-base-600 hover:bg-base-500">Cancel</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ open: boolean; message: string }>()
defineEmits(['confirm','cancel'])
</script>


