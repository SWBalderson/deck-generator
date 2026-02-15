import { defineConfig } from 'unocss'

export default defineConfig({
  theme: {
    colors: {
      primary: '#003366',
      secondary: '#6699CC',
      accent: '#FF6B35',
      background: '#FFFFFF',
      text: '#333333',
      'text-light': '#666666',
      border: '#E5E5E5',
      grid: '#F5F5F5',
    },
    fontFamily: {
      sans: 'Inter, system-ui, sans-serif',
      serif: 'Georgia, "Times New Roman", serif',
    },
  },
  shortcuts: {
    'slide-title': 'font-serif text-2xl text-primary font-semibold mb-6',
    'slide-text': 'text-base leading-relaxed text-text',
    'slide-grid': 'grid grid-cols-2 gap-8 items-start mt-4',
    'chart-container': 'w-full max-h-[400px]',
    'slide-source': 'absolute bottom-6 right-8 text-xs text-text-light italic',
  },
})
