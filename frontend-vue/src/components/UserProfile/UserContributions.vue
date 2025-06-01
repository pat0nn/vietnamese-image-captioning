<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { useToast } from 'vue-toastification';
import { useAuthStore } from '../../stores/auth';
import { getUserContributions, deleteContribution, updateContribution } from '../../utils/requestHelper';
import { API_URL } from '../../constants';

const contributions = ref([]);
const isLoading = ref(true);
const error = ref(null);
const editItem = ref(null);
const editedCaption = ref('');
const isSaving = ref(false);
const validationError = ref(null);
const fullSizeImage = ref(null);
const openDropdownId = ref(null);

const authStore = useAuthStore();
const toast = useToast();

// Fetch user contributions
const fetchContributions = async () => {
  isLoading.value = true;
  error.value = null;
  
  try {
    const response = await getUserContributions();
    console.log('Raw API response:', response);
    
    // Process contributions to ensure consistent field names
    if (response.contributions && Array.isArray(response.contributions)) {
      contributions.value = response.contributions.map(item => {
        console.log('Processing contribution item:', item);
        // Create a normalized item with consistent field names
        return {
          ...item,
          // Ensure image_path exists (may be called image in some responses)
          image_path: item.image_path || item.image,
          // Ensure caption exists (may be called user_caption in some responses)
          caption: item.caption || item.user_caption,
          // Ensure image_id is available - CRITICAL for API calls
          image_id: item.image_id || item.id
        };
      });
      
      console.log('Processed contributions with normalized fields:', contributions.value);
      
      // Test image URLs for diagnostic purposes
      if (contributions.value.length > 0) {
        testImageUrls(contributions.value[0]);
      }
    } else {
      contributions.value = [];
    }
    
    console.log('Processed contributions:', contributions.value);
  } catch (err) {
    console.error('Error fetching contributions:', err);
    error.value = 'Không thể tải danh sách đóng góp của bạn';
    toast.error(error.value);
  } finally {
    isLoading.value = false;
  }
};

// Delete a contribution
const handleDeleteContribution = async (contributionId) => {
  if (!confirm('Bạn có chắc chắn muốn xóa đóng góp này không?')) {
    return;
  }
  
  try {
    console.log(`Attempting to delete contribution with ID: ${contributionId}`);
    
    // Tìm item để lấy thông tin chính xác về contribution_id
    const itemToDelete = contributions.value.find(item => 
      item.id === contributionId || item.contribution_id === contributionId
    );
    
    if (!itemToDelete) {
      throw new Error('Không tìm thấy đóng góp để xóa');
    }
    
    // Ưu tiên sử dụng contribution_id (chính là id trong bảng contributions)
    const idToUse = itemToDelete.contribution_id || contributionId;
    console.log('Deleting contribution with ID:', idToUse, '(Original ID:', contributionId, ')');
    console.log('Full item data:', itemToDelete);
    
    // Xóa contribution bằng contribution_id
    await deleteContribution(idToUse);
    
    // Remove from local list - check both id fields for compatibility
    contributions.value = contributions.value.filter(
      item => item.id !== contributionId && item.contribution_id !== contributionId
    );
    toast.success('Đã xóa đóng góp thành công');
  } catch (err) {
    console.error('Error deleting contribution:', err);
    toast.error('Không thể xóa đóng góp');
  }
};

// Validate caption
const validateCaption = (caption) => {
  // Check for empty caption
  if (!caption || !caption.trim()) {
    return {
      isValid: false,
      error: 'Vui lòng nhập mô tả cho hình ảnh.'
    };
  }

  // Split caption into words (ignore consecutive spaces)
  const words = caption.trim().split(/\s+/);
  
  // Check minimum word count
  if (words.length < 5) {
    return {
      isValid: false,
      error: 'Mô tả phải có ít nhất 5 từ.'
    };
  }
  
  // Check word length
  const longWords = words.filter(word => word.length > 7);
  if (longWords.length > 0) {
    return {
      isValid: false,
      error: `Không được sử dụng từ dài quá 7 ký tự: ${longWords.join(', ')}`
    };
  }
  
  return {
    isValid: true,
    error: null
  };
};

// Edit a contribution
const handleEdit = (item) => {
  editItem.value = item;
  editedCaption.value = item.caption || '';
  validationError.value = null;
  openDropdownId.value = null;
};

// Cancel editing
const handleCancelEdit = () => {
  editItem.value = null;
  editedCaption.value = '';
  validationError.value = null;
};

// Save edited caption
const handleSaveEdit = async (contributionId) => {
  // Validate caption
  const validationResult = validateCaption(editedCaption.value);
  if (!validationResult.isValid) {
    validationError.value = validationResult.error;
    return;
  }

  try {
    isSaving.value = true;
    validationError.value = null;
    
    // Tìm item đang sửa để lấy image_id đúng
    const itemToUpdate = contributions.value.find(item => 
      item.id === contributionId || item.contribution_id === contributionId
    );
    
    if (!itemToUpdate) {
      throw new Error('Không tìm thấy đóng góp để cập nhật');
    }
    
    // Ưu tiên sử dụng image_id
    const idToUse = itemToUpdate.image_id || contributionId;
    console.log('Updating contribution with ID:', idToUse, '(Original ID:', contributionId, ')');
    console.log('Full item data:', itemToUpdate);
    
    // Update caption on server using image_id
    await updateContribution(idToUse, editedCaption.value);
    
    // Update locally after successful API call
    contributions.value = contributions.value.map(item => {
      // If this is the item we're updating
      if (item.id === contributionId || item.contribution_id === contributionId) {
        return { 
          ...item, 
          caption: editedCaption.value,
          user_caption: editedCaption.value // Update both fields for compatibility
        };
      }
      return item;
    });
    
    editItem.value = null;
    toast.success('Cập nhật mô tả thành công');
  } catch (err) {
    console.error('Error updating caption:', err);
    toast.error(`Không thể cập nhật mô tả: ${err.message || 'Lỗi không xác định'}`);
  } finally {
    isSaving.value = false;
  }
};

// Open full size image
const openFullSize = (item) => {
  // Get the image path from either property
  const imagePath = item.image_path || item.image;
  
  // Check if image path exists
  if (!imagePath) {
    toast.error('Không tìm thấy hình ảnh');
    return;
  }
  
  // Try the URL to verify the image can load
  const imageUrl = getImageUrl(item);
  const img = new Image();
  
  img.onerror = () => {
    console.error('Failed to load image:', imageUrl);
    toast.error('Không thể tải hình ảnh');
  };
  
  img.onload = () => {
    fullSizeImage.value = {
      src: imageUrl,
      alt: item.caption || 'Hình ảnh đóng góp',
      caption: item.caption || 'Không có mô tả'
    };
  };
  
  img.src = imageUrl;
};

// Get proper image URL with fallback
const getImageUrl = (item) => {
  console.log('Getting URL for item:', item);
  
  // Check if item exists and has image data
  if (!item || (!item.image && !item.image_path)) {
    console.log('No image or image_path found in item');
    return '/placeholder-image.svg'; // Fallback image
  }
  
  // If path already starts with http, return as is
  if ((item.image && item.image.startsWith('http')) || 
      (item.image_path && item.image_path.startsWith('http'))) {
    const url = item.image || item.image_path;
    console.log('Using full URL:', url);
    return url;
  }
  
  // Get the image path from either property
  const imagePath = item.image_path || item.image;
  
  // Sử dụng đường dẫn tuyệt đối thay vì tương đối
  // Ví dụ: https://vic-api.phambatrong.com/uploads/file.jpg thay vì /uploads/file.jpg
  return `${API_URL}/uploads/${imagePath}`;
};

// Close full size image
const closeFullSize = () => {
  fullSizeImage.value = null;
};

// Toggle dropdown
const toggleDropdown = (e, contributionId) => {
  e.stopPropagation();
  openDropdownId.value = openDropdownId.value === contributionId ? null : contributionId;
};

// Handle click outside to close dropdown
const handleClickOutside = () => {
  openDropdownId.value = null;
};

// Handle modal click
const handleModalContentClick = (e) => {
  e.stopPropagation();
};

// For testing only - remove in production
const testImageUrls = async (item) => {
  if (!item) return;
  
  const paths = [
    `/uploads/${item.image_path || item.image}`,
    `/api/uploads/${item.image_path || item.image}`,
    `/uploads/${item.image}`,
    `/api/uploads/${item.image}`
  ];
  
  console.log('Testing image URLs for:', item);
  
  for (const path of paths) {
    if (!path.includes('undefined')) {
      const fullUrl = `${API_URL}${path}`;
      console.log(`Testing URL: ${fullUrl}`);
      
      try {
        const img = new Image();
        img.onload = () => console.log(`✅ URL works: ${fullUrl}`);
        img.onerror = () => console.log(`❌ URL failed: ${fullUrl}`);
        img.src = fullUrl;
      } catch (err) {
        console.error(`Error testing ${fullUrl}:`, err);
      }
    }
  }
};

onMounted(() => {
  if (authStore.isAuthenticated) {
    fetchContributions();
  }
  
  // Add event listener for click outside
  document.addEventListener('click', handleClickOutside);
});

onBeforeUnmount(() => {
  // Clean up the event listener
  document.removeEventListener('click', handleClickOutside);
});
</script>

<template>
  <div class="contributions-container">
    <h2 class="text-2xl font-bold mb-6 text-gray-800 pb-2 border-b border-gray-200">Các đóng góp của bạn</h2>
    
    <div v-if="isLoading" class="text-center py-8 text-gray-600">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-2 border-gray-300 border-t-blue-600 mb-2"></div>
      <p>Đang tải đóng góp của bạn...</p>
    </div>
    
    <div v-else-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded text-center my-4">
      {{ error }}
    </div>
    
    <div v-else-if="contributions.length === 0" class="text-center py-8 bg-gray-100 rounded-lg my-4 text-gray-600">
      Bạn chưa có đóng góp nào.
    </div>
    
    <div v-else>
      <div 
        v-for="contribution in contributions" 
        :key="contribution.id" 
        class="bg-white rounded-lg shadow-md overflow-hidden mb-6 border border-gray-200 flex flex-col md:flex-row relative"
      >
        <!-- Action Dropdown -->
        <div class="absolute top-2 right-2 z-10">
          <button 
            @click="(e) => toggleDropdown(e, contribution.id)" 
            class="bg-gray-200 hover:bg-gray-300 rounded-full p-2 flex items-center justify-center"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
            </svg>
          </button>
          
          <div 
            v-if="openDropdownId === contribution.id" 
            class="absolute right-0 top-10 bg-white shadow-lg rounded-md overflow-hidden border border-gray-200 w-36"
            @click.stop
          >
            <button 
              @click="() => handleEdit(contribution)" 
              class="flex items-center w-full px-4 py-2 text-left hover:bg-gray-100 text-gray-700"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 0L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              Sửa mô tả
            </button>
            <button 
              @click="() => handleDeleteContribution(contribution.id)" 
              class="flex items-center w-full px-4 py-2 text-left hover:bg-gray-100 text-red-600"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              Xóa đóng góp
            </button>
          </div>
        </div>
        
        <!-- Image -->
        <div 
          class="w-full md:w-64 h-48 overflow-hidden cursor-pointer"
          @click="() => openFullSize(contribution)"
        >
          <img 
            :src="getImageUrl(contribution)" 
            :alt="contribution.caption || 'Hình ảnh đóng góp'" 
            class="w-full h-full object-cover"
            @error="(e) => e.target.src = '/placeholder-image.svg'"
          />
        </div>
        
        <!-- Details -->
        <div class="p-4 flex-1">
          <!-- Edit Form -->
          <div v-if="editItem && editItem.id === contribution.id" class="w-full">
            <textarea
              v-model="editedCaption"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 mb-3"
              placeholder="Nhập mô tả mới cho hình ảnh này..."
              rows="4"
            ></textarea>
            
            <div v-if="validationError" class="text-red-500 text-sm mb-3 p-2 bg-red-50 rounded-md">
              {{ validationError }}
            </div>
            
            <div class="flex space-x-3">
              <button 
                @click="() => handleSaveEdit(contribution.id)"
                class="px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 focus:outline-none"
                :disabled="isSaving"
                :class="{ 'opacity-70 cursor-not-allowed': isSaving }"
              >
                {{ isSaving ? 'Đang lưu...' : 'Lưu' }}
              </button>
              <button 
                @click="handleCancelEdit"
                class="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 focus:outline-none"
              >
                Hủy
              </button>
            </div>
          </div>
          
          <!-- Display Content -->
          <div v-else>
            <div class="mb-3">
              <h3 class="text-sm text-gray-600 mb-1 font-medium">Mô tả của bạn:</h3>
              <p class="text-gray-800 bg-gray-50 p-3 rounded border-l-4 border-blue-500">{{ contribution.caption || "Không có mô tả" }}</p>
            </div>
            
            <div v-if="contribution.ai_caption" class="mb-3">
              <h3 class="text-sm text-gray-600 mb-1 font-medium">Mô tả AI:</h3>
              <p class="text-gray-800 bg-gray-50 p-3 rounded border-l-4 border-green-500">{{ contribution.ai_caption }}</p>
            </div>
            
            <div class="text-sm text-gray-500">
              <p>Thời gian: {{ new Date(contribution.createdAt || contribution.created_at).toLocaleString() }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Full Size Image Modal -->
    <div 
      v-if="fullSizeImage" 
      class="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50 p-4 animate-fade-in"
      @click="closeFullSize"
    >
      <div 
        class="bg-white rounded-lg max-w-3xl max-h-[90vh] flex flex-col overflow-hidden shadow-xl"
        @click="handleModalContentClick"
      >
        <button 
          class="absolute top-4 right-4 bg-black bg-opacity-50 text-white rounded-full w-8 h-8 flex items-center justify-center hover:bg-opacity-70"
          @click="closeFullSize"
        >
          &times;
        </button>
        
        <div class="overflow-auto max-h-[70vh] flex items-center justify-center p-4">
          <img 
            :src="fullSizeImage.src" 
            :alt="fullSizeImage.alt" 
            class="max-w-full max-h-full object-contain"
            @error="(e) => e.target.src = '/placeholder-image.svg'"
          />
        </div>
        
        <div class="p-4 border-t border-gray-200">
          <h3 class="text-sm text-gray-600 mb-1 font-medium">Mô tả:</h3>
          <p class="text-gray-800 bg-gray-50 p-3 rounded border-l-4 border-blue-500">{{ fullSizeImage.caption }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.contributions-container {
  padding: 20px;
  max-width: 900px;
  margin: 0 auto;
}

.animate-fade-in {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style> 