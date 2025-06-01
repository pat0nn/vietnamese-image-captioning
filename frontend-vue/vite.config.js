import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    allowedHosts: ['vic.phambatrong.com'],
    proxy: {
      // Proxy API requests in development
      '/api': {
        target: 'https://flask-backend-668247880976.asia-east1.run.app',
        changeOrigin: true,
      },
      // Proxy uploads in development
      '/uploads': {
        target: 'https://flask-backend-668247880976.asia-east1.run.app',
        changeOrigin: true,
      }
    }
  },
})
