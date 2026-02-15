<template>
  <div class="slide-source">
    Source: <slot />
  </div>
</template>

<style>
.slide-source {
  position: absolute;
  bottom: 1.5rem;
  right: 2rem;
  font-size: 0.75rem;
  color: #666;
  font-style: italic;
}
</style>
