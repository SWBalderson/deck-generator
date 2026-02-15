<template>
  <img :src="logoSrc" class="slide-logo" alt="Logo" @error="handleError" />
</template>

<script setup>
import { computed, ref } from 'vue'

const candidates = [
  '/logo-title.svg',
  '/logo-title.png',
  '/logo-title.webp',
  '/logo-title.jpg',
  '/logo-title.jpeg',
  '/logo.svg',
  '/logo.png',
  '/logo.webp',
  '/logo.jpg',
  '/logo.jpeg',
]
const current = ref(0)

const logoSrc = computed(() => candidates[current.value])

const handleError = () => {
  if (current.value < candidates.length - 1)
    current.value += 1
}
</script>

<style scoped>
.slide-logo {
  position: absolute;
  top: 1.25rem;
  left: 1.5rem;
  height: 30px;
  max-width: 140px;
  width: auto;
  object-fit: contain;
  display: block;
  z-index: 20;
  pointer-events: none;
}
</style>
