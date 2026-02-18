<template>
  <h2 class="slide-title">
    <slot />
  </h2>
</template>

<style>
.slide-title {
  font-family: Georgia, serif;
  font-size: 1.75rem;
  color: var(--slide-primary, #003366);
  margin-bottom: 1.5rem;
  line-height: 1.3;
  font-weight: 600;
}
</style>
