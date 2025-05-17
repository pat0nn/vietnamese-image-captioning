<template>
  <div class="dashboard-card">
    <div class="flex justify-between items-center mb-4">
      <h3 class="text-xl font-bold leading-none text-gray-900 dark:text-white">Lịch sử tạo Caption</h3>
    </div>
    
    <!-- Search and filters -->
    <div class="flex flex-col md:flex-row items-center justify-between space-y-3 md:space-y-0 md:space-x-4 py-4">
      <div class="w-full md:w-1/2">
        <form class="flex items-center" @submit.prevent="handleSearch">
          <label for="simple-search" class="sr-only">Tìm kiếm</label>
          <div class="relative w-full">
            <div class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
              <svg aria-hidden="true" class="w-5 h-5 text-gray-500 dark:text-gray-400" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd"></path>
              </svg>
            </div>
            <input 
              v-model="searchQuery" 
              type="text" 
              id="simple-search" 
              class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full pl-10 p-2 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500" 
              placeholder="Tìm kiếm caption..." 
            >
          </div>
        </form>
      </div>
      
      <!-- Star Rating Filter -->
      <div class="w-full md:w-auto flex flex-col md:flex-row space-y-2 md:space-y-0 items-stretch md:items-center">
        <label for="rating-filter" class="text-sm font-medium text-gray-700 dark:text-gray-300 mr-2 self-center whitespace-nowrap">
          Lọc theo sao:
        </label>
        <div class="inline-flex rounded-md shadow-sm" role="group">
          <button 
            v-for="rating in 5" 
            :key="`rating-filter-${rating}`" 
            type="button" 
            :class="[
              'px-3 py-2 text-sm font-medium border',
              selectedRating === rating 
                ? 'bg-blue-500 text-white border-blue-600 hover:bg-blue-600' 
                : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-100 dark:bg-gray-800 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-700',
              rating === 1 ? 'rounded-l-lg' : '',
              rating === 5 ? 'rounded-r-lg' : ''
            ]"
            @click="toggleRatingFilter(rating)"
          >
            {{ rating }} <span class="text-yellow-400">★</span>
          </button>
        </div>
        <button 
          v-if="selectedRating !== null"
          type="button" 
          class="ml-2 text-sm text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
          @click="clearRatingFilter"
        >
          Xóa bộ lọc
        </button>
      </div>
    </div>
    
    <!-- Loading indicator -->
    <div v-if="loading" class="flex justify-center items-center py-10">
      <svg class="animate-spin -ml-1 mr-3 h-10 w-10 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    </div>
    
    <!-- Error message -->
    <div v-else-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
      <strong class="font-bold">Lỗi!</strong>
      <span class="block sm:inline"> {{ error }}</span>
    </div>
    
    <!-- Empty state -->
    <div v-else-if="captions.length === 0" class="text-center py-10">
      <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 13h6m-3-3v6m-9 1V7a2 2 0 012-2h14a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2z" />
      </svg>
      <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">Không có caption</h3>
      <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
        Chưa có caption nào được tạo hoặc không tìm thấy kết quả phù hợp.
      </p>
    </div>
    
    <!-- Caption Grid -->
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6 gap-4 auto-rows-auto">
      <div v-for="caption in filteredCaptions" :key="caption.image_id" class="bg-white rounded-lg border border-gray-200 shadow-md dark:bg-gray-800 dark:border-gray-700">
        <div class="relative">
          <img 
            class="rounded-t-lg h-48 w-full object-cover cursor-pointer" 
            :src="getImageUrl(caption.image_path)" 
            :alt="caption.ai_caption"
            @click="openImageModal(caption)">
          <div class="absolute top-2 right-2 flex items-center space-x-2">
            <div class="flex items-center bg-gray-900 bg-opacity-75 text-yellow-400 text-xs font-semibold rounded px-2 py-1">
              <span class="mr-1">{{ Number(caption.average_rating).toFixed(1) }}</span>
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"></path>
              </svg>
            </div>
            
            <!-- Action menu -->
            <button 
              @click="toggleActionMenu(caption.image_id)"
              data-action-menu
              class="inline-flex items-center p-1 text-sm font-medium text-center text-gray-900 bg-white rounded-lg hover:bg-gray-100 focus:ring-4 focus:outline-none dark:text-white focus:ring-gray-50 dark:bg-gray-800 dark:hover:bg-gray-700 dark:focus:ring-gray-600"
            >
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z"></path>
              </svg>
            </button>
            
            <!-- Dropdown menu -->
            <div 
              v-if="activeActionMenu === caption.image_id" 
              class="absolute right-0 top-10 z-10 mt-2 w-44 bg-white rounded-md shadow-lg py-1 ring-1 ring-black ring-opacity-5 focus:outline-none dark:bg-gray-700 dark:divide-gray-600"
            >
              <button 
                @click="confirmDelete(caption)"
                class="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-600"
              >
                <svg class="w-4 h-4 mr-2 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                Xóa
              </button>
            </div>
          </div>
        </div>
        
        <div class="p-5">
          <div class="flex items-center mb-3">
            <svg class="w-4 h-4 text-gray-400 mr-1" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
              <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd"></path>
            </svg>
            <span class="text-sm text-gray-600 dark:text-gray-400">
              {{ caption.username || 'Ẩn danh' }}
            </span>
            <span class="text-xs text-gray-500 ml-2">
              {{ formatDate(caption.created_at) }}
            </span>
          </div>
          
          <p class="mb-3 font-normal text-gray-700 dark:text-gray-400">{{ caption.ai_caption }}</p>
          
          <div v-if="caption.user_rating" class="flex items-center mt-4">
            <span class="text-sm text-gray-600 dark:text-gray-400 mr-2">Đánh giá của bạn:</span>
            <div class="flex text-yellow-400">
              <template v-for="star in 5" :key="`user-rating-${star}`">
                <svg 
                  :class="[star <= caption.user_rating ? 'text-yellow-400' : 'text-gray-300 dark:text-gray-600']"
                  class="w-4 h-4" 
                  fill="currentColor" 
                  viewBox="0 0 20 20" 
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"></path>
                </svg>
              </template>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Pagination -->
    <div class="flex flex-col md:flex-row justify-between items-center space-y-3 md:space-y-0 mt-4">
      <span class="text-sm text-gray-700 dark:text-gray-400">
        Hiển thị từ <span class="font-semibold text-gray-900 dark:text-white">{{ (page - 1) * limit + 1 }}</span> đến 
        <span class="font-semibold text-gray-900 dark:text-white">{{ Math.min(page * limit, totalItems) }}</span> trong số 
        <span class="font-semibold text-gray-900 dark:text-white">{{ totalItems }}</span> ảnh.
      </span>
      <nav aria-label="Page navigation">
        <ul class="inline-flex items-center -space-x-px">
          <li>
            <button 
              @click="changePage(page - 1)" 
              :disabled="page === 1"
              :class="[
                'block px-3 py-2 ml-0 leading-tight border rounded-l-lg',
                page === 1 
                  ? 'text-gray-400 cursor-not-allowed bg-gray-100 border-gray-300 dark:bg-gray-700 dark:border-gray-700 dark:text-gray-500' 
                  : 'text-gray-500 bg-white border-gray-300 hover:bg-gray-100 hover:text-gray-700 dark:bg-gray-800 dark:border-gray-700 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-white'
              ]">
              <span class="sr-only">Trang trước</span>
              <svg class="w-5 h-5" aria-hidden="true" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd"></path>
              </svg>
            </button>
          </li>
          <li v-for="pageNum in paginationRange" :key="pageNum">
            <button 
              @click="changePage(pageNum)"
              :class="[
                'px-3 py-2 leading-tight border',
                pageNum === page 
                  ? 'z-10 text-blue-600 border-blue-300 bg-blue-50 dark:border-gray-700 dark:bg-gray-700 dark:text-white' 
                  : 'text-gray-500 bg-white border-gray-300 hover:bg-gray-100 hover:text-gray-700 dark:bg-gray-800 dark:border-gray-700 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-white'
              ]">
              {{ pageNum }}
            </button>
          </li>
          <li>
            <button 
              @click="changePage(page + 1)" 
              :disabled="page === totalPages"
              :class="[
                'block px-3 py-2 leading-tight border rounded-r-lg',
                page === totalPages 
                  ? 'text-gray-400 cursor-not-allowed bg-gray-100 border-gray-300 dark:bg-gray-700 dark:border-gray-700 dark:text-gray-500' 
                  : 'text-gray-500 bg-white border-gray-300 hover:bg-gray-100 hover:text-gray-700 dark:bg-gray-800 dark:border-gray-700 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-white'
              ]">
              <span class="sr-only">Trang tiếp</span>
              <svg class="w-5 h-5" aria-hidden="true" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"></path>
              </svg>
            </button>
          </li>
        </ul>
      </nav>
    </div>
  </div>
  
  <!-- Full Size Image Modal -->
  <div 
    v-if="fullSizeImage" 
    class="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50 p-4 animate-fade-in"
    @click="closeImageModal"
  >
    <div 
      class="bg-white rounded-lg max-w-5xl max-h-[90vh] flex flex-col overflow-hidden shadow-xl"
      @click.stop
    >
      <button 
        class="absolute top-4 right-4 bg-black bg-opacity-50 text-white rounded-full w-10 h-10 flex items-center justify-center hover:bg-opacity-70 text-2xl"
        @click="closeImageModal"
      >
        &times;
      </button>
      
      <div class="overflow-auto p-4 flex items-center justify-center">
        <img 
          :src="fullSizeImage ? getImageUrl(fullSizeImage.image_path) : ''"
          :alt="fullSizeImage ? fullSizeImage.ai_caption : ''"
          class="max-w-full max-h-[70vh] object-contain"
        />
      </div>
      
      <div class="p-6 border-t border-gray-200">
        <div class="mb-4">
          <h3 class="text-sm text-gray-600 mb-1 font-medium">AI Caption:</h3>
          <p class="text-gray-800 bg-gray-50 p-3 rounded border-l-4 border-blue-500">
            {{ fullSizeImage ? fullSizeImage.ai_caption : '' }}
          </p>
        </div>
        
        <div v-if="fullSizeImage && fullSizeImage.user_rating" class="flex items-center mt-4">
          <span class="text-sm text-gray-600 dark:text-gray-400 mr-2">Đánh giá:</span>
          <div class="flex text-yellow-400">
            <template v-for="star in 5" :key="`modal-rating-${star}`">
              <svg 
                :class="[fullSizeImage && star <= fullSizeImage.user_rating ? 'text-yellow-400' : 'text-gray-300 dark:text-gray-600']"
                class="w-5 h-5" 
                fill="currentColor" 
                viewBox="0 0 20 20" 
                xmlns="http://www.w3.org/2000/svg"
              >
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"></path>
              </svg>
            </template>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <!-- Delete Confirmation Modal -->
  <div v-if="showDeleteConfirmation" class="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
    <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-4 text-center sm:block sm:p-0">
      <!-- Background overlay -->
      <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="cancelDelete"></div>
      
      <!-- Modal panel -->
      <div class="inline-block align-middle bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all mx-auto my-8 max-w-lg dark:bg-gray-800">
        <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4 dark:bg-gray-800">
          <div class="sm:flex sm:items-start">
            <div class="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10 dark:bg-red-600">
              <svg class="h-6 w-6 text-red-600 dark:text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
              <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-white" id="modal-title">
                Xác nhận xóa
              </h3>
              <div class="mt-2">
                <p class="text-sm text-gray-500 dark:text-gray-400">
                  Bạn có chắc chắn muốn xóa caption này? Hành động này không thể hoàn tác.
                </p>
              </div>
            </div>
          </div>
        </div>
        <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse dark:bg-gray-700">
          <button 
            type="button" 
            class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-red-600 text-base font-medium text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 sm:ml-3 sm:w-auto sm:text-sm"
            @click="deleteCaption"
          >
            Xóa
          </button>
          <button 
            type="button" 
            class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm dark:bg-gray-600 dark:text-white dark:border-gray-500 dark:hover:bg-gray-700"
            @click="cancelDelete"
          >
            Hủy
          </button>
        </div>
      </div>
    </div>
  </div>
  
  <!-- Toast Notification -->
  <div v-if="showToast" class="fixed bottom-4 right-4 bg-green-500 text-white px-4 py-2 rounded shadow-lg z-50 animate-fade-in">
    {{ toastMessage }}
  </div>
</template>

<script>
import { ref, computed, onMounted, watch, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../../stores/admin/auth';
import { fetchCaptionHistory, deleteCaptionHistory } from '../../utils/adminApi';
import { API_URL } from '../../constants';

export default {
  name: 'CaptionHistoryView',
  setup() {
    const router = useRouter();
    const authStore = useAuthStore();
    const apiUrl = API_URL;
    
    // Function to get the correct URL for images
    const getImageUrl = (imagePath) => {
      // If API_URL is empty (relative mode) or we're on the same domain
      if (apiUrl === '') {
        return `/uploads/${imagePath}`;
      }
      // Otherwise use the full URL
      return `${apiUrl}/uploads/${imagePath}`;
    };
    
    // State
    const captions = ref([]);
    const loading = ref(false);
    const error = ref(null);
    const searchQuery = ref('');
    const selectedRating = ref(null);
    const page = ref(1);
    const limit = ref(10);
    const totalItems = ref(0);
    const fullSizeImage = ref(null);
    
    // Add these new state variables for action menu and deletion
    const activeActionMenu = ref(null);
    const captionToDelete = ref(null);
    const showDeleteConfirmation = ref(false);
    const showToast = ref(false);
    const toastMessage = ref('');
    
    // Toggle action menu
    const toggleActionMenu = (imageId) => {
      if (activeActionMenu.value === imageId) {
        activeActionMenu.value = null;
      } else {
        activeActionMenu.value = imageId;
      }
    };
    
    // Handle click outside to close active menu
    const handleClickOutside = (event) => {
      // Check if click is outside the action menu button
      if (activeActionMenu.value && !event.target.closest('[data-action-menu]')) {
        activeActionMenu.value = null;
      }
    };
    
    // Show delete confirmation modal
    const confirmDelete = (caption) => {
      captionToDelete.value = caption;
      showDeleteConfirmation.value = true;
      activeActionMenu.value = null; // Close menu
    };
    
    // Cancel delete
    const cancelDelete = () => {
      captionToDelete.value = null;
      showDeleteConfirmation.value = false;
    };
    
    // Delete caption
    const deleteCaption = async () => {
      if (!captionToDelete.value) return;
      
      try {
        const response = await deleteCaptionHistory(captionToDelete.value.image_id);
        
        if (response.success) {
          // Remove from list
          captions.value = captions.value.filter(
            item => item.image_id !== captionToDelete.value.image_id
          );
          
          // Update total count
          totalItems.value--;
          
          // Show success toast
          toastMessage.value = 'Caption đã được xóa thành công!';
          showToast.value = true;
          setTimeout(() => {
            showToast.value = false;
          }, 3000);
        } else {
          // Show error toast
          toastMessage.value = `Lỗi: ${response.error}`;
          showToast.value = true;
          setTimeout(() => {
            showToast.value = false;
          }, 3000);
        }
      } catch (err) {
        console.error('Error deleting caption:', err);
        
        // Show error toast
        toastMessage.value = 'Có lỗi xảy ra khi xóa caption';
        showToast.value = true;
        setTimeout(() => {
          showToast.value = false;
        }, 3000);
      } finally {
        // Close modal
        showDeleteConfirmation.value = false;
        captionToDelete.value = null;
      }
    };
    
    // Filtered captions based on search query
    const filteredCaptions = computed(() => {
      if (!searchQuery.value) return captions.value;
      
      const query = searchQuery.value.toLowerCase();
      return captions.value.filter(caption => {
        return (
          (caption.ai_caption && caption.ai_caption.toLowerCase().includes(query)) ||
          (caption.user_caption && caption.user_caption.toLowerCase().includes(query)) ||
          (caption.username && caption.username.toLowerCase().includes(query))
        );
      });
    });
    
    // Calculate total pages for pagination
    const totalPages = computed(() => {
      return Math.ceil(totalItems.value / limit.value);
    });
    
    // Generate pagination range
    const paginationRange = computed(() => {
      const range = [];
      const maxVisiblePages = 5;
      
      // If less than max visible pages, show all
      if (totalPages.value <= maxVisiblePages) {
        for (let i = 1; i <= totalPages.value; i++) {
          range.push(i);
        }
        return range;
      }
      
      // Calculate start and end based on current page
      let start = Math.max(1, page.value - Math.floor(maxVisiblePages / 2));
      let end = start + maxVisiblePages - 1;
      
      // Adjust if end exceeds total pages
      if (end > totalPages.value) {
        end = totalPages.value;
        start = Math.max(1, end - maxVisiblePages + 1);
      }
      
      for (let i = start; i <= end; i++) {
        range.push(i);
      }
      
      return range;
    });
    
    // Format date for display
    const formatDate = (dateString) => {
      if (!dateString) return '';
      
      // Tạo đối tượng date và điều chỉnh múi giờ +7 cho Việt Nam
      const date = new Date(dateString);
      // Thêm 7 giờ để chuyển từ UTC sang múi giờ Việt Nam (UTC+7)
      const vietnamTime = new Date(date.getTime() + 7 * 60 * 60 * 1000);
      
      return new Intl.DateTimeFormat('vi-VN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
      }).format(vietnamTime);
    };
    
    // Fetch captions based on current filters and pagination
    const loadCaptions = async () => {
      loading.value = true;
      error.value = null;
      
      try {
        const params = {
          page: page.value,
          limit: limit.value,
          ai_only: true // Chỉ lấy những ảnh có AI caption
        };
        
        // Thêm filter theo rating nếu có
        if (selectedRating.value !== null) {
          params.rating = selectedRating.value;
        }
        
        const response = await fetchCaptionHistory(params);
        
        if (!response.success) {
          throw new Error(response.error || 'Failed to load caption history');
        }
        
        captions.value = response.data.captions;
        totalItems.value = response.data.total;
      } catch (err) {
        console.error('Error loading caption history:', err);
        error.value = err.message || 'Failed to load caption history';
      } finally {
        loading.value = false;
      }
    };
    
    // Handle search submission
    const handleSearch = () => {
      // We're handling client-side filtering in the computed property
      // so no need to reload data
    };
    
    // Change page
    const changePage = (newPage) => {
      if (newPage < 1 || newPage > totalPages.value) {
        return;
      }
      
      page.value = newPage;
      loadCaptions();
    };
    
    // Open full size image modal
    const openImageModal = (caption) => {
      fullSizeImage.value = caption;
      document.body.style.overflow = 'hidden'; // Prevent scrolling when modal is open
    };
    
    // Close full size image modal
    const closeImageModal = () => {
      fullSizeImage.value = null;
      document.body.style.overflow = ''; // Re-enable scrolling
    };
    
    // Toggle rating filter
    const toggleRatingFilter = (rating) => {
      if (selectedRating.value === rating) {
        selectedRating.value = null;
      } else {
        selectedRating.value = rating;
      }
      // Reset to first page when changing filters
      page.value = 1;
      loadCaptions();
    };
    
    // Clear rating filter
    const clearRatingFilter = () => {
      selectedRating.value = null;
      loadCaptions();
    };
    
    // Register click outside handler
    onMounted(() => {
      loadCaptions();
      document.addEventListener('click', handleClickOutside);
    });
    
    // Remove event listener on unmount
    onUnmounted(() => {
      document.removeEventListener('click', handleClickOutside);
    });
    
    return {
      apiUrl,
      getImageUrl,
      captions,
      filteredCaptions,
      loading,
      error,
      searchQuery,
      selectedRating,
      page,
      limit,
      totalItems,
      totalPages,
      paginationRange,
      formatDate,
      handleSearch,
      changePage,
      fullSizeImage,
      openImageModal,
      closeImageModal,
      toggleRatingFilter,
      clearRatingFilter,
      
      // Add new properties and methods for action menu
      activeActionMenu,
      toggleActionMenu,
      showDeleteConfirmation,
      confirmDelete,
      cancelDelete,
      deleteCaption,
      showToast,
      toastMessage
    };
  }
};
</script>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style> 