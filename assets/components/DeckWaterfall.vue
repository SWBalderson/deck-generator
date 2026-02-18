<template>
  <div class="chart-container">
    <canvas :id="chartId"></canvas>
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

onMounted(async () => {
  const response = await fetch(props.data)
  const waterfallData = await response.json()
  
  const ctx = document.getElementById(chartId.value).getContext('2d')
  
  // Waterfall chart implementation
  const data = {
    labels: waterfallData.labels,
    datasets: [{
      label: waterfallData.label || 'Value',
      data: waterfallData.values,
      backgroundColor: waterfallData.values.map(v => {
        const style = getComputedStyle(document.documentElement)
        return v >= 0
          ? (style.getPropertyValue('--slide-primary').trim() || '#003366')
          : (style.getPropertyValue('--slide-accent').trim() || '#FF6B35')
      }),
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
          grid: { color: getComputedStyle(document.documentElement).getPropertyValue('--slide-grid').trim() || '#E5E5E5' },
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
})
</script>
