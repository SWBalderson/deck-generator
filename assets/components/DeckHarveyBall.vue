<template>
  <div class="harvey-ball">
    <span v-for="n in 3" :key="n" 
          class="ball"
          :class="{ 'filled': n <= filled, 'empty': n > filled }">
    </span>
    <span class="label">{{ label }}</span>
  </div>
</template>

<script setup>
const props = defineProps({
  filled: {
    type: Number,
    default: 0,
    validator: (v) => v >= 0 && v <= 3
  },
  label: {
    type: String,
    default: ''
  }
})
</script>

<style>
.harvey-ball {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
}

.ball {
  width: 1rem;
  height: 1rem;
  border-radius: 50%;
  border: 2px solid var(--slide-secondary, #6699CC);
}

.ball.filled {
  background-color: var(--slide-secondary, #6699CC);
}

.ball.empty {
  background-color: transparent;
}

.label {
  margin-left: 0.5rem;
  font-size: 0.9rem;
  color: var(--slide-text, #333);
}
</style>
