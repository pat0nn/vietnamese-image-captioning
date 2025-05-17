import { defineStore } from 'pinia'

export const useDarkModeStore = defineStore('darkMode', {
  state: () => ({
    isDarkMode: true
  }),
  
  actions: {
    initialize() {
      // Check for saved preference
      const savedMode = localStorage.getItem('darkMode')
      if (savedMode !== null) {
        this.isDarkMode = savedMode === 'true'
      } else {
        // Default to system preference
        this.isDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches
      }
      
      this.applyDarkMode()
    },
    
    toggle() {
      this.isDarkMode = !this.isDarkMode
      localStorage.setItem('darkMode', this.isDarkMode)
      this.applyDarkMode()
    },
    
    applyDarkMode() {
      if (this.isDarkMode) {
        document.documentElement.classList.add('dark')
      } else {
        document.documentElement.classList.remove('dark')
      }
    }
  }
}) 