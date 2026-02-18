<template>
  <div class="chart-container">
    <canvas v-if="!error" :id="chartId"></canvas>
    <div v-else class="chart-error">{{ error }}</div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import Chart from 'chart.js/auto'

const props = defineProps({
  data: {
    type: String,
    required: true
  }
})

const chartId = ref(`waterfall-${Math.random().toString(36).substr(2, 9)}`)
const error = ref(null)

function resolveColor(varName, fallback) {
  return getComputedStyle(document.documentElement).getPropertyValue(varName).trim() || fallback
}

onMounted(async () => {
  try {
    const response = await fetch(props.data)
    if (!response.ok) {
      error.value = `Failed to load chart data (${response.status})`
      return
    }

    const waterfallData = await response.json()

    if (!waterfallData?.labels?.length || !waterfallData?.values?.length) {
      error.value = 'Chart data is missing labels or values'
      return
    }

    if (waterfallData.labels.length !== waterfallData.values.length) {
      error.value = 'Chart labels and values must have equal length'
      return
    }

    const ctx = document.getElementById(chartId.value)?.getContext('2d')
    if (!ctx) {
      error.value = 'Canvas element not found'
      return
    }

    const primaryColour = resolveColor('--slide-primary', '#003366')
    const accentColour = resolveColor('--slide-accent', '#FF6B35')
    const gridColour = resolveColor('--slide-grid', '#E5E5E5')

    const data = {
      labels: waterfallData.labels,
      datasets: [{
        label: waterfallData.label || 'Value',
        data: waterfallData.values,
        backgroundColor: waterfallData.values.map(v => v >= 0 ? primaryColour : accentColour),
        borderWidth: 0
      }]
    }

    new Chart(ctx, {
      type: 'bar',
      data: data,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        indexAxis: 'y',
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (context) => {
                const val = context.raw
                return val >= 0 ? `+${val}` : `${val}`
              }
            }
          }
        },
        scales: {
          x: {
            grid: { color: gridColour },
            ticks: {
              callback: (val) => val >= 0 ? `+${val}` : val
            }
          },
          y: {
            grid: { display: false }
          }
        }
      }
    })
  } catch (e) {
    error.value = `Chart rendering failed: ${e.message}`
    console.error('[DeckWaterfall]', e)
  }
})
</script>

<style scoped>
.chart-error {
  padding: 1rem;
  color: var(--slide-accent, #FF6B35);
  font-style: italic;
  text-align: center;
}
</style>
