<template>
  <div class="flex flex-col items-center justify-center px-6 h-screen mx-auto dark:bg-gray-900">
    <div class="text-center">
      <h1 class="mb-4 text-7xl font-bold text-blue-600 dark:text-blue-500">404</h1>
      <p class="mb-4 text-3xl font-bold text-gray-900 dark:text-white">Không tìm thấy trang</p>
      <p class="mb-8 text-lg text-gray-500 dark:text-gray-400">Xin lỗi, chúng tôi không thể tìm thấy trang bạn đang tìm kiếm.</p>
      <div class="flex flex-col sm:flex-row gap-4 justify-center">
        <router-link to="/admin" class="inline-flex items-center justify-center px-5 py-3 text-base font-medium text-center text-white bg-blue-700 rounded-lg hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 dark:focus:ring-blue-900">
          Trang quản trị
          <svg class="w-5 h-5 ml-2 -mr-1" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
            <path fill-rule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clip-rule="evenodd"></path>
          </svg>
        </router-link>
        <router-link to="/" class="inline-flex items-center justify-center px-5 py-3 text-base font-medium text-center text-white bg-green-600 rounded-lg hover:bg-green-700 focus:ring-4 focus:ring-green-300 dark:focus:ring-green-900">
          Trang chủ chính
          <svg class="w-5 h-5 ml-2 -mr-1" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
            <path fill-rule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clip-rule="evenodd"></path>
          </svg>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NotFound',
  mounted() {
  }
}
</script> 