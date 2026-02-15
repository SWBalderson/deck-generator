<template>
  <div class="slidev-layout h-full p-8 pt-20">
    <DeckLogo />
    <slot />
  </div>
</template>

<script setup>
import DeckLogo from '../components/DeckLogo.vue'
</script>
