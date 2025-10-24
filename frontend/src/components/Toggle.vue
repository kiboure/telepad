<template>
  <div class="flex justify-center mb-4">
    <div class="relative inline-flex p-1 bg-base-800 rounded-full shadow-innerdeep">
      <button
        :class="btnClass('library')"
        @click="$emit('update:modelValue', 'library')"
      >Library</button>
      <button
        :class="btnClass('search')"
        @click="$emit('update:modelValue', 'search')"
      >Search</button>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{ modelValue: 'library' | 'search' }>()

const btnClass = (tab: 'library' | 'search') => [
  'px-5 py-2 rounded-full transition-all',
  props.modelValue === tab
    ? 'bg-base-600 text-accent-300 shadow'
    : 'text-accent-500 hover:text-accent-300'
]
</script>


