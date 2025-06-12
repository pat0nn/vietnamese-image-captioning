<script setup>
import Footer from '../components/Footer.vue';
</script>

<template>
  <div class="page-container">
    <div class="flex items-center justify-center py-12 bg-gray-50 dark:bg-gray-900 flex-grow">
    <div class="w-full max-w-md px-6 py-12 bg-white shadow-md rounded-lg dark:bg-gray-800">
      <div class="text-center">
        <h1 class="mb-4 text-7xl font-bold text-gray-800 dark:text-gray-200">404</h1>
        <h2 class="mb-8 text-2xl font-medium text-gray-600 dark:text-gray-400">Trang không tồn tại</h2>
        <p class="mb-8 text-gray-500 dark:text-gray-500">Trang bạn đang tìm kiếm không tồn tại hoặc đã bị di chuyển.</p>
        <router-link to="/" class="px-5 py-3 text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500">
          Trở về trang chủ
        </router-link>
      </div>
    </div>
    </div>
    
    <Footer />
  </div>
</template>

<style scoped>
.page-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.flex-grow {
  flex: 1;
}

/* Mobile-specific styles to push footer down */
@media (max-width: 768px) {
  .page-container {
    min-height: 120vh;
  }
  
  .flex-grow {
    min-height: 100vh;
    padding-bottom: 2rem;
  }
}

@media (max-width: 480px) {
  .page-container {
    min-height: 130vh;
  }
  
  .flex-grow {
    min-height: 110vh;
    padding-bottom: 3rem;
  }
}
</style>

<script>
export default {
  name: 'NotFound'
}
</script> 