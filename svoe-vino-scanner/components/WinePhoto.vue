<script setup lang="ts">
const props = withDefaults(defineProps<{ src: string; name: string; priority?: boolean }>(), { priority: false })
const failed = ref(false)
watch(() => props.src, () => { failed.value = false })
</script>
<template>
  <div class="wine-photo">
    <img v-if="src && !failed" :src="src" :alt="name" :loading="priority ? 'eager' : 'lazy'" :fetchpriority="priority ? 'high' : 'auto'" decoding="async" referrerpolicy="no-referrer" @error="failed = true" />
    <div v-else class="photo-unavailable"><ResultIcon name="search" /><span>Фото пока недоступно</span></div>
  </div>
</template>
