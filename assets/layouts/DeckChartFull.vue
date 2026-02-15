<template>
  <div class="slidev-layout h-full p-8 pt-20 flex flex-col">
    <DeckLogo />
    <h2 class="slide-title mb-4"><slot name="title" /></h2>
    <div class="flex-1 flex items-center justify-center">
      <slot name="chart" />
    </div>
    <div class="slide-source">
      <slot name="source" />
    </div>
  </div>
</template>

<script setup>
import DeckLogo from '../components/DeckLogo.vue'
</script>
