import './assets/main.css'
import './assets/admin-style.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import Toast from 'vue-toastification'
import 'vue-toastification/dist/index.css'
import 'flowbite'

import App from './App.vue'
import router from './router'

const app = createApp(App)
const pinia = createPinia()

// Toast options
const toastOptions = {
  position: 'bottom-right',
  timeout: 3000,
  closeOnClick: true,
  pauseOnHover: true,
  draggable: true,
  draggablePercent: 0.6,
  showCloseButtonOnHover: false,
  hideProgressBar: false,
  closeButton: 'button',
}

app.use(pinia)
app.use(router)
app.use(Toast, toastOptions)

// Import ApexCharts for admin dashboard charts
import VueApexCharts from 'vue3-apexcharts'
app.use(VueApexCharts)

app.mount('#app')
