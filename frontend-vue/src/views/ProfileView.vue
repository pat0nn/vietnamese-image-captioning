<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import UserContributions from '../components/UserProfile/UserContributions.vue';
import ProfileEdit from '../components/UserProfile/ProfileEdit.vue';
import AuthNav from '../components/Auth/AuthNav.vue';
import Footer from '../components/Footer.vue';
import { BASE_URL } from '../constants';

const router = useRouter();
const authStore = useAuthStore();
const activeTab = ref('profile'); // Default tab: 'profile' or 'contributions'

// Redirect to home if not authenticated
const checkAuth = () => {
  if (!authStore.isLoading && !authStore.isAuthenticated) {
    router.push('/');
  }
};

onMounted(() => {
  checkAuth();
  
  // Set page title
  document.title = 'Hồ sơ của tôi - Ứng dụng Mô tả Hình ảnh';
});

// Watch for auth state changes
watch(() => authStore.isAuthenticated, (isAuthenticated) => {
  if (!isAuthenticated) {
    router.push('/');
  }
});
</script>

<template>
  <div v-if="authStore.isLoading" class="flex justify-center items-center h-screen">
    <div class="text-center">
      <div class="inline-block animate-spin rounded-full h-10 w-10 border-2 border-gray-300 border-t-blue-600"></div>
      <p class="mt-2 text-gray-600">Đang tải...</p>
    </div>
  </div>
  
  <template v-else-if="authStore.isAuthenticated">
    <div class="page-container">
      <!-- Navigation Bar -->
      <div class="bg-white shadow-md px-6 py-4 flex justify-between items-center">
        <router-link to="/" class="flex items-center truncate cursor-pointer">
          <h1 class="text-xl font-bold text-blue-500">Hệ Thống Chú Thích Hình Ảnh</h1>
        </router-link>
        <AuthNav />
      </div>
      
      <!-- Main Content -->
      <main class="max-w-[900px] mx-auto px-4 py-8 flex-grow">
        <!-- Tabs Navigation -->
        <div class="flex border-b border-gray-200 mb-6">
          <button 
            @click="activeTab = 'profile'" 
            class="py-2 px-4 font-medium text-sm focus:outline-none"
            :class="activeTab === 'profile' ? 'text-blue-600 border-b-2 border-blue-500' : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'"
          >
            Thông tin cá nhân
          </button>
          <button 
            @click="activeTab = 'contributions'" 
            class="py-2 px-4 font-medium text-sm focus:outline-none ml-4"
            :class="activeTab === 'contributions' ? 'text-blue-600 border-b-2 border-blue-500' : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'"
          >
            Đóng góp của tôi
          </button>
        </div>
        
        <!-- Tab Content -->
        <div v-if="activeTab === 'profile'">
          <ProfileEdit />
        </div>
        <div v-else-if="activeTab === 'contributions'">
          <UserContributions />
        </div>
      </main>
      
      <!-- Footer -->
      <Footer />
    </div>
  </template>
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

main {
  padding: 20px;
  max-width: 900px;
  margin: 0 auto;
}
</style> 