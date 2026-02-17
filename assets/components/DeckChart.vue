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
  try {
    const response = await fetch(props.data)
    if (!response.ok)
      throw new Error(`HTTP ${response.status} for ${props.data}`)

    const chartConfig = await response.json()
    const resolvedType = chartConfig.type || props.type
    const resolvedData = chartConfig.data || chartConfig
    const resolvedOptions = {
      responsive: true,
      maintainAspectRatio: false,
      ...(chartConfig.options || {}),
      ...props.options,
      plugins: {
        legend: {
          display: resolvedData.datasets?.length > 1,
        },
        ...((chartConfig.options && chartConfig.options.plugins) || {}),
        ...(props.options.plugins || {}),
      },
    }

    const canvas = document.getElementById(chartId.value)
    if (!canvas)
      throw new Error(`Canvas element not found for ${chartId.value}`)

    const ctx = canvas.getContext('2d')
    if (!ctx)
      throw new Error(`2D context unavailable for ${chartId.value}`)

    new Chart(ctx, {
      type: resolvedType,
      data: resolvedData,
      options: resolvedOptions,
    })
  }
  catch (error) {
    console.error('[DeckChart] Failed to render chart', {
      dataPath: props.data,
      requestedType: props.type,
      error,
    })
  }
})
</script>

<style>
.chart-container {
  width: 100%;
  height: 100%;
  max-height: 400px;
}
</style>
