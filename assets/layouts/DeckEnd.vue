<template>
  <div class="slidev-layout center h-full flex flex-col justify-center items-center text-center">
    <DeckLogo />
    <h1 class="text-5xl font-serif font-bold text-primary mb-8">Thank You</h1>
    <div class="text-2xl text-text-light">
      <slot />
    </div>
  </div>
</template>

<script setup>
import DeckLogo from '../components/DeckLogo.vue'
</script>
