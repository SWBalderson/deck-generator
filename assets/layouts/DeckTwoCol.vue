<template>
  <div class="slidev-layout h-full p-8 pt-20">
    <DeckLogo />
    <h2 class="slide-title text-center mb-8"><slot name="title" /></h2>
    <div class="two-cols">
      <div class="col-left">
        <slot name="left" />
      </div>
      <div class="col-right">
        <slot name="right" />
      </div>
    </div>
  </div>
</template>

<script setup>
import DeckLogo from '../components/DeckLogo.vue'
</script>

<style>
.two-cols {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 3rem;
  height: calc(100% - 6rem);
  align-items: start;
}
</style>
