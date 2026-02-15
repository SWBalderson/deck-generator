<template>
  <div class="slidev-layout center h-full flex flex-col justify-center items-center text-center">
    <DeckLogo />
    <h1 class="text-4xl font-serif font-bold text-primary mb-4"><slot /></h1>
    <div class="text-xl text-text-light mt-4">
      <slot name="subtitle" />
    </div>
    <div class="text-base text-text-light mt-8">
      <slot name="author" />
    </div>
  </div>
</template>

<script setup>
import DeckLogo from '../components/DeckLogo.vue'
</script>
