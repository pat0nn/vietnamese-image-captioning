<template>
  <div class="dashboard-card">
    <h2 class="text-xl font-bold mb-4 text-gray-900 dark:text-white">Tải xuống dữ liệu đã được duyệt</h2>
    
    <!-- Statistics card -->
    <div class="bg-white rounded-lg border border-gray-200 shadow-md p-6 mb-6 dark:bg-gray-800 dark:border-gray-700">
      <div class="flex items-center justify-between">
        <div>
          <h3 class="text-lg font-semibold text-gray-700 dark:text-white">Số lượng ảnh đã được chấp nhận</h3>
          <div class="flex items-center mt-2">
            <span class="text-3xl font-bold text-blue-600 dark:text-blue-400">{{ approvedCount }}</span>
            <span v-if="loading" class="ml-3">
              <svg class="animate-spin h-5 w-5 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </span>
          </div>
          <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
            Dữ liệu cập nhật {{ lastUpdated }}
          </p>
        </div>
        <div>
          <svg class="w-12 h-12 text-blue-500" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
            <path fill-rule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clip-rule="evenodd"></path>
          </svg>
        </div>
      </div>
    </div>
    
    <!-- Download section -->
    <div class="bg-white rounded-lg border border-gray-200 shadow-md p-6 dark:bg-gray-800 dark:border-gray-700">
      <h3 class="text-lg font-semibold text-gray-700 dark:text-white mb-4">Tải xuống dữ liệu</h3>
      <p class="text-gray-600 dark:text-gray-300 mb-6">
        Tạo và tải xuống tệp zip chứa tất cả hình ảnh đã được chấp nhận và file JSON với các mô tả tương ứng.
      </p>
      
      <div class="flex items-center space-x-4">
        <button 
          @click="generateDownloadPackage" 
          class="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
          :disabled="generating || !approvedCount"
        >
          <svg v-if="generating" class="animate-spin -ml-1 mr-2 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <svg v-else class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
            <path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd"></path>
          </svg>
          {{ generating ? "Đang tạo..." : "Tạo và tải xuống" }}
        </button>
        
        <button 
          v-if="downloadUrl"
          @click="downloadPackage" 
          class="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
        >
          <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
            <path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd"></path>
          </svg>
          Tải xuống lại
        </button>
      </div>
    </div>
    
    <!-- Status messages -->
    <div v-if="error" class="mt-4 bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded" role="alert">
      <p class="font-bold">Lỗi</p>
      <p>{{ error }}</p>
    </div>
    
    <div v-if="success" class="mt-4 bg-green-100 border-l-4 border-green-500 text-green-700 p-4 rounded" role="alert">
      <p class="font-bold">Thành công</p>
      <p>{{ success }}</p>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { API_URL } from '../../constants';
import axios from 'axios';

export default {
  name: 'DownloadView',
  setup() {
    const approvedCount = ref(0);
    const loading = ref(false);
    const generating = ref(false);
    const error = ref(null);
    const success = ref(null);
    const lastUpdated = ref('');
    const downloadUrl = ref(null);
    
    // Format date
    const formatDate = (date) => {
      return new Intl.DateTimeFormat('vi-VN', {
        year: 'numeric',
        month: 'numeric',
        day: 'numeric',
        hour: 'numeric',
        minute: 'numeric'
      }).format(date);
    };
    
    // Get approved contributions count
    const fetchApprovedCount = async () => {
      loading.value = true;
      error.value = null;
      
      try {
        const response = await axios.get(`${API_URL}/api/admin/contributions/count?status=approved`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('auth_token') || localStorage.getItem('token')}`
          }
        });
        
        if (response.data.success) {
          approvedCount.value = response.data.count;
          lastUpdated.value = formatDate(new Date());
        } else {
          error.value = response.data.error || 'Không thể lấy số lượng ảnh đã duyệt';
        }
      } catch (err) {
        console.error('Error fetching approved count:', err);
        error.value = err.response?.data?.error || 'Đã xảy ra lỗi khi lấy số liệu';
      } finally {
        loading.value = false;
      }
    };
    
    // Generate download package
    const generateDownloadPackage = async () => {
      generating.value = true;
      error.value = null;
      success.value = null;
      
      try {
        const response = await axios.post(
          `${API_URL}/api/admin/download/generate`,
          {},
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('auth_token') || localStorage.getItem('token')}`
            },
            responseType: 'blob'
          }
        );
        
        // Create a URL for the blob
        const blob = new Blob([response.data], { type: 'application/zip' });
        downloadUrl.value = URL.createObjectURL(blob);
        
        // Trigger download
        const link = document.createElement('a');
        link.href = downloadUrl.value;
        link.download = `approved-images-${new Date().toISOString().split('T')[0]}.zip`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        success.value = 'Tệp zip đã được tạo và tải xuống thành công!';
      } catch (err) {
        console.error('Error generating download package:', err);
        error.value = 'Đã xảy ra lỗi khi tạo tệp zip. Vui lòng thử lại sau.';
      } finally {
        generating.value = false;
      }
    };
    
    // Download the package again
    const downloadPackage = () => {
      if (!downloadUrl.value) return;
      
      const link = document.createElement('a');
      link.href = downloadUrl.value;
      link.download = `approved-images-${new Date().toISOString().split('T')[0]}.zip`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    };
    
    // Load data on component mount
    onMounted(() => {
      fetchApprovedCount();
    });
    
    return {
      approvedCount,
      loading,
      generating,
      error,
      success,
      lastUpdated,
      downloadUrl,
      generateDownloadPackage,
      downloadPackage
    };
  }
};
</script> 