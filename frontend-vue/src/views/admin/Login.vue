<template>
  <div class="admin-login-container">
    <div class="admin-login-content">
      <div class="flex flex-col items-center justify-center px-6 pt-8 mx-auto md:h-screen pt:mt-0 dark:bg-gray-900">
        <a href="/" class="flex items-center justify-center mb-8 text-2xl font-semibold lg:mb-10 dark:text-white">
          <span>Hệ Thống Chú Thích Hình Ảnh</span>  
        </a>
        <!-- Card -->
        <div class="w-full max-w-xl p-6 space-y-8 sm:p-8 bg-white rounded-lg shadow dark:bg-gray-800">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white">
            Đăng nhập vào Bảng Điều Khiển Admin
          </h2>
          
          <!-- Error Alert -->
          <div v-if="authStore.error" class="flex p-4 mb-4 text-sm text-red-800 border border-red-300 rounded-lg bg-red-50 dark:bg-gray-800 dark:text-red-400 dark:border-red-800" role="alert">
            <svg aria-hidden="true" class="flex-shrink-0 inline w-5 h-5 mr-3" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path></svg>
            <span class="sr-only">Lỗi</span>
            <div>
              <span class="font-medium" :class="{'text-lg': authStore.error.includes('admin')}">{{ authStore.error }}</span>
              <div v-if="authStore.error.includes('admin')" class="mt-2">
                <p>Vui lòng sử dụng tài khoản admin hoặc liên hệ quản trị viên để được cấp quyền.</p>
              </div>
            </div>
          </div>
          
          <form class="mt-8 space-y-6" @submit.prevent="handleLogin">
            <div>
              <label for="username" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">Tên đăng nhập</label>
              <input v-model="formData.username" type="text" name="username" id="username" class="bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500" placeholder="Tên đăng nhập" required />
            </div>
            <div>
              <label for="password" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">Mật khẩu</label>
              <input v-model="formData.password" type="password" name="password" id="password" placeholder="••••••••" class="bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm rounded-lg focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500" required />
            </div>
            <div class="flex items-start">
              <div class="flex items-center h-5">
                <input v-model="formData.remember" id="remember" aria-describedby="remember" name="remember" type="checkbox" class="w-4 h-4 border-gray-300 rounded bg-gray-50 focus:ring-3 focus:ring-primary-300 dark:focus:ring-primary-600 dark:ring-offset-gray-800 dark:bg-gray-700 dark:border-gray-600" />
              </div>
              <div class="ml-3 text-sm">
                <label for="remember" class="font-medium text-gray-900 dark:text-white">Ghi nhớ đăng nhập</label>
              </div>
              <router-link to="/forgot-password" class="ml-auto text-sm text-blue-600 hover:underline dark:text-blue-500">Quên mật khẩu?</router-link>
            </div>
            <button type="submit" class="w-full px-5 py-3 text-base font-medium text-center text-white bg-blue-700 rounded-lg hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 sm:w-auto dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800" :disabled="authStore.loading">
              <span v-if="authStore.loading" class="flex items-center justify-center">
                <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Đang đăng nhập...
              </span>
              <span v-else>Đăng nhập</span>
            </button>
            <div class="text-sm font-medium text-gray-500 dark:text-gray-400">
              Chưa có tài khoản? <router-link to="/register" class="text-blue-600 hover:underline dark:text-blue-500">Tạo tài khoản</router-link>
            </div>
          </form>
        </div>
      </div>
    </div>
    
    <!-- Footer (appears when scrolling) -->
    <Footer />
  </div>
</template>

<script>
import { useAuthStore } from '../../stores/admin/auth'
import Footer from '../../components/Footer.vue'

export default {
  name: 'Login',
  components: {
    Footer
  },
  data() {
    return {
      formData: {
        username: '',
        password: '',
        remember: false
      }
    }
  },
  setup() {
    const authStore = useAuthStore()
    return { authStore }
  },
  methods: {
    async handleLogin() {
      // Clear any previous errors
      this.authStore.clearError()
      
      // Attempt login through the auth store
      await this.authStore.login(
        this.formData.username,
        this.formData.password,
        this.formData.remember
      )
    }
  },
  created() {
    // Check if there's a redirect reason in the query params
    const redirectReason = this.$route.query.reason
    if (redirectReason === 'session_expired') {
      this.authStore.error = 'Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.'
    } else if (redirectReason === 'unauthorized') {
      this.authStore.error = 'Vui lòng đăng nhập để truy cập trang này.'
    }
    
    // Check if remembered login
    const remembered = localStorage.getItem('remember_login') === 'true'
    if (remembered) {
      this.formData.remember = true
    }
  }
}
</script>

<style scoped>
.admin-login-container {
  min-height: 150vh; /* Make container tall enough for scrolling */
  display: flex;
  flex-direction: column;
}

.admin-login-content {
  flex: 1;
  min-height: 120vh; /* Ensure login content takes enough space */
}
</style> 