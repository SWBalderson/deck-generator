<template>
  <div class="chart-container">
    <canvas :id="chartId"></canvas>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import Chart from 'chart.js/auto'

const props = defineProps({
  type: {
    type: String,
    required: true
  },
  data: {
    type: String,
    required: true
  },
  options: {
    type: Object,
    default: () => ({})
  }
})

const chartId = ref(`chart-${Math.random().toString(36).substr(2, 9)}`)

onMounted(async () => {
  const response = await fetch(props.data)
  const chartData = await response.json()
  
  const ctx = document.getElementById(chartId.value).getContext('2d')
  
  new Chart(ctx, {
    type: props.type,
    data: chartData,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: chartData.datasets?.length > 1
        }
      },
      ...props.options
    }
  })
})
</script>

<style>
.chart-container {
  width: 100%;
  height: 100%;
  max-height: 400px;
}
</style>
