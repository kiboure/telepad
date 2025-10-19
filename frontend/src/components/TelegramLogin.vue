<template>
  <div ref="container" class="w-full flex items-center justify-center"></div>
</template>

<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref } from 'vue'

const container = ref<HTMLElement | null>(null)
let scriptEl: HTMLScriptElement | null = null
let observer: MutationObserver | null = null

onMounted(() => {
  // Expose the onAuth callback expected by the Telegram widget
  ;(window as any).onTelegramAuth = function(user: any) {
    window.dispatchEvent(new CustomEvent('tg-auth', { detail: user }))
  }

  // Inject widget script into our container so it renders in place
  scriptEl = document.createElement('script')
  scriptEl.async = true
  scriptEl.src = 'https://telegram.org/js/telegram-widget.js?22'
  ;(scriptEl as any).setAttribute('data-telegram-login', 'tlpadbot')
  ;(scriptEl as any).setAttribute('data-size', 'large')
  ;(scriptEl as any).setAttribute('data-userpic', 'false')
  ;(scriptEl as any).setAttribute('data-radius', '8')
  ;(scriptEl as any).setAttribute('data-onauth', 'onTelegramAuth(user)')
  ;(scriptEl as any).setAttribute('data-request-access', 'write')
  container.value?.appendChild(scriptEl)

  // Center the resulting iframe the widget injects
  observer = new MutationObserver(() => {
    const iframe = container.value?.querySelector('iframe[src*="telegram.org/js/telegram-widget"]') as HTMLIFrameElement | null
    if (iframe) {
      iframe.style.display = 'inline-block'
      iframe.style.position = 'static'
      iframe.style.margin = '0 auto'
      iframe.style.transform = 'none'
    }
  })
  if (container.value) observer.observe(container.value, { childList: true, subtree: true })
})

onBeforeUnmount(() => {
  if (observer) observer.disconnect()
  if (container.value) container.value.innerHTML = ''
  if (scriptEl?.parentNode) scriptEl.parentNode.removeChild(scriptEl)
})
</script>


