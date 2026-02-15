<template>
  <div class="slidev-layout section-slide h-full flex flex-col justify-center items-center text-center p-8 pt-20">
    <DeckLogo />
    <div class="section-content">
      <slot />
    </div>
  </div>
</template>

<script setup>
import DeckLogo from '../components/DeckLogo.vue'
</script>

<style scoped>
.section-content :deep(h1) {
  font-family: Georgia, serif;
  color: #003366;
  font-size: 2.75rem;
  font-weight: 600;
  line-height: 1.2;
  margin: 0;
}

.section-content :deep(h2) {
  font-family: Georgia, serif;
  color: #003366;
  font-size: 1.6rem;
  font-weight: 600;
  line-height: 1.3;
  margin-top: 1rem;
}
</style>
