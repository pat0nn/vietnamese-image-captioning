<template>
  <div class="flex items-center justify-center min-h-screen py-12 bg-gray-50 dark:bg-gray-900">
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
</template>

<script>
export default {
  name: 'NotFound'
}
</script> 