<template>
  <img v-if="!hidden" :src="logoSrc" class="slide-logo" alt="Logo" @error="handleError" />
</template>

<script setup>
import { computed, ref } from 'vue'

const LOGO_CANDIDATES = [
  '/logo-title.svg',
  '/logo-title.png',
  '/logo.svg',
  '/logo.png',
  '/images/logo-title.svg',
  '/images/logo-title.png',
  '/images/logo.svg',
  '/images/logo.png',
]

const current = ref(0)
const hidden = ref(false)

const logoSrc = computed(() => LOGO_CANDIDATES[current.value])

const handleError = () => {
  if (current.value < LOGO_CANDIDATES.length - 1) {
    current.value += 1
  } else {
    hidden.value = true
  }
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
