<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue';
import { useToast } from 'vue-toastification';
import { useAuthStore } from '../../stores/auth';
import axios from 'axios';
import { API_URL } from '../../constants';

const authStore = useAuthStore();
const toast = useToast();

// User data - direct reference to the store
const user = computed(() => authStore.currentUser);
// Simple refs for form inputs
const usernameInput = ref('');
const fullNameInput = ref('');
const currentPassword = ref('');
const newPassword = ref('');
const confirmPassword = ref('');

// UI states
const isUpdatingProfile = ref(false);
const isUpdatingPassword = ref(false);
const isUpdatingAvatar = ref(false);
const avatarFile = ref(null);
const avatarPreview = ref(null);
const errors = ref({
  username: '',
  fullName: '',
  currentPassword: '',
  newPassword: '',
  confirmPassword: '',
  avatar: ''
});

// Get avatar URL
const avatarUrl = computed(() => {
  // Debug user data
  console.log('Avatar computed property - User data:', user.value);
  console.log('Avatar value:', user.value?.avatar);
  
  if (avatarPreview.value) {
    console.log('Using avatar preview');
    return avatarPreview.value;
  }
  
  if (user.value?.avatar) {
    // If avatar is a full URL (starts with http), use it directly
    if (user.value.avatar.startsWith('http')) {
      console.log('Using HTTP avatar URL');
      // Add cache-busting parameter to prevent caching
      const url = user.value.avatar.includes('?') 
        ? user.value.avatar 
        : `${user.value.avatar}?t=${Date.now()}`;
      return url;
    } else {
      // Otherwise, construct the full URL
      const url = `${API_URL}/uploads/avatars/${user.value.avatar}?t=${Date.now()}`;
      console.log('Generated avatar URL:', url);
      return url;
    }
  }
  
  console.log('Using default avatar');
  return '/user_9970571.svg'; // Default avatar
});

// Handle avatar loading errors
const handleAvatarError = (e) => {
  console.error('Avatar loading error:', e);
  // Set the target's src to the local fallback image
  e.target.src = '/user_9970571.svg';
};

// Handle avatar file selection
const handleAvatarChange = (event) => {
  const file = event.target.files[0];
  if (!file) return;
  
  // Check file size (max 5MB)
  if (file.size > 5 * 1024 * 1024) {
    errors.value.avatar = 'Kích thước file quá lớn (tối đa 5MB)';
    return;
  }
  
  // Check file type
  const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/jpg'];
  if (!allowedTypes.includes(file.type)) {
    errors.value.avatar = 'Chỉ chấp nhận file hình ảnh (JPEG, PNG, GIF)';
    return;
  }
  
  // Clear previous error
  errors.value.avatar = '';
  
  // Set file for upload
  avatarFile.value = file;
  
  // Create preview
  const reader = new FileReader();
  reader.onload = (e) => {
    avatarPreview.value = e.target.result;
  };
  reader.readAsDataURL(file);
};

// Form input variables were already declared above

// Initialize form values from user data
const initFormValues = () => {
  console.log('Initializing form values from user:', user.value);
  if (user.value) {
    usernameInput.value = user.value.username || '';
    fullNameInput.value = user.value.full_name || '';
    console.log('Form values initialized:', { username: usernameInput.value, fullName: fullNameInput.value });
  }
};

// Handle the user-profile-updated custom event
const handleProfileUpdated = (event) => {
  console.log('Received user-profile-updated event:', event.detail);
  if (event.detail) {
    // Update the form inputs
    usernameInput.value = event.detail.username || '';
    fullNameInput.value = event.detail.full_name || '';
    console.log('Form values updated from event:', { username: usernameInput.value, fullName: fullNameInput.value });
  }
};

// Initialize form values when component is mounted
onMounted(() => {
  // Thêm console log để debug
  console.log('ProfileEdit mounted, user from store:', authStore.currentUser);
  
  // Refresh user data from API
  authStore.refreshUserProfile();
  
  // Initialize form values
  initFormValues();
  
  // Listen for user profile updates
  window.addEventListener('user-profile-updated', handleProfileUpdated);
});

// Clean up event listener when component is unmounted
onBeforeUnmount(() => {
  window.removeEventListener('user-profile-updated', handleProfileUpdated);
});

// Watch for changes in user data and update form values
watch(() => user.value, (newUser, oldUser) => {
  console.log('User data changed in store:', newUser);
  console.log('Previous user data:', oldUser);
  if (newUser) {
    usernameInput.value = newUser.username || '';
    fullNameInput.value = newUser.full_name || '';
    console.log('Form values updated from watch:', { username: usernameInput.value, fullName: fullNameInput.value });
  }
}, { deep: true, immediate: true });

// Update profile information
const updateProfile = async () => {
  // Validate
  errors.value.username = '';
  errors.value.fullName = '';
  
  if (!usernameInput.value.trim()) {
    errors.value.username = 'Tên đăng nhập không được để trống';
    return;
  }
  
  isUpdatingProfile.value = true;
  
  try {
    const response = await axios.put(
      `${API_URL}/api/profile/update`,
      {
        username: usernameInput.value.trim(),
        full_name: fullNameInput.value.trim()
      },
      {
        headers: {
          'Authorization': `Bearer ${authStore.token}`
        }
      }
    );
    
    console.log('Profile update response:', response.data);
    if (response.data.success) {
      // Update local user data
      if (response.data.user) {
        console.log('Updating user profile with:', response.data.user);
        // Update user profile in store
        authStore.updateUserProfile(response.data.user);
        
        // Update input values directly to match the returned data
        if (response.data.user.full_name) {
          fullNameInput.value = response.data.user.full_name;
        }
        if (response.data.user.username) {
          usernameInput.value = response.data.user.username;
        }
        
        // Update token if username changed
        if (response.data.token) {
          authStore.updateToken(response.data.token);
        }
      }
      
      toast.success('Thông tin hồ sơ đã được cập nhật');
      
      // Force a refresh of the user data after a short delay
      setTimeout(() => {
        authStore.refreshUserProfile();
      }, 500);
    } else {
      toast.error(response.data.error || 'Không thể cập nhật thông tin');
    }
  } catch (error) {
    console.error('Error updating profile:', error);
    const errorMessage = error.response?.data?.error || 'Đã xảy ra lỗi khi cập nhật thông tin';
    toast.error(errorMessage);
    
    if (error.response?.data?.error === 'Tên đăng nhập đã tồn tại') {
      errors.value.username = 'Tên đăng nhập đã tồn tại';
    }
  } finally {
    isUpdatingProfile.value = false;
  }
};

// Update password
const updatePassword = async () => {
  // Validate
  errors.value.currentPassword = '';
  errors.value.newPassword = '';
  errors.value.confirmPassword = '';
  
  if (!currentPassword.value) {
    errors.value.currentPassword = 'Vui lòng nhập mật khẩu hiện tại';
    return;
  }
  
  if (!newPassword.value) {
    errors.value.newPassword = 'Vui lòng nhập mật khẩu mới';
    return;
  }
  
  if (newPassword.value.length < 6) {
    errors.value.newPassword = 'Mật khẩu mới phải có ít nhất 6 ký tự';
    return;
  }
  
  if (newPassword.value !== confirmPassword.value) {
    errors.value.confirmPassword = 'Xác nhận mật khẩu không khớp';
    return;
  }
  
  isUpdatingPassword.value = true;
  
  try {
    const response = await axios.put(
      `${API_URL}/api/profile/update-password`,
      {
        currentPassword: currentPassword.value,
        newPassword: newPassword.value
      },
      {
        headers: {
          'Authorization': `Bearer ${authStore.token}`
        }
      }
    );
    
    if (response.data.success) {
      toast.success('Mật khẩu đã được cập nhật');
      // Clear password fields
      currentPassword.value = '';
      newPassword.value = '';
      confirmPassword.value = '';
    } else {
      toast.error(response.data.error || 'Không thể cập nhật mật khẩu');
    }
  } catch (error) {
    console.error('Error updating password:', error);
    const errorMessage = error.response?.data?.error || 'Đã xảy ra lỗi khi cập nhật mật khẩu';
    toast.error(errorMessage);
    
    if (error.response?.data?.error === 'Mật khẩu hiện tại không đúng') {
      errors.value.currentPassword = 'Mật khẩu hiện tại không đúng';
    }
  } finally {
    isUpdatingPassword.value = false;
  }
};

// Update avatar
const updateAvatar = async () => {
  if (!avatarFile.value) {
    errors.value.avatar = 'Vui lòng chọn file ảnh đại diện';
    return;
  }
  
  isUpdatingAvatar.value = true;
  
  try {
    // Create form data
    const formData = new FormData();
    formData.append('avatar', avatarFile.value);
    
    const response = await axios.post(
      `${API_URL}/api/profile/update-avatar`,
      formData,
      {
        headers: {
          'Authorization': `Bearer ${authStore.token}`,
          'Content-Type': 'multipart/form-data'
        }
      }
    );
    
    if (response.data.success) {
      console.log('Avatar update success response:', response.data);
      
      // Update local user data
      if (response.data.user) {
        // If we have an avatar_url in the response, use it directly
        if (response.data.avatar_url) {
          const userData = {
            ...response.data.user,
            avatar: response.data.avatar_url // Override with the full URL
          };
          console.log('Updating user with avatar URL:', userData);
          authStore.updateUserProfile(userData);
          
          // Force refresh the avatar preview
          avatarPreview.value = response.data.avatar_url + '?t=' + Date.now();
        } else {
          // Otherwise just update with the user data
          authStore.updateUserProfile(response.data.user);
        }
      }
      
      toast.success('Ảnh đại diện đã được cập nhật');
      
      // Clear file input and preview
      avatarFile.value = null;
      avatarPreview.value = null;
      
      // Reset file input
      const fileInput = document.getElementById('avatar-upload');
      if (fileInput) {
        fileInput.value = '';
      }
      
      // Force a refresh of the avatar
      setTimeout(() => {
        console.log('Forcing avatar refresh');
        const avatarImg = document.querySelector('.avatar-container img');
        if (avatarImg) {
          const currentSrc = avatarImg.src;
          avatarImg.src = currentSrc.includes('?') ? currentSrc : `${currentSrc}?t=${Date.now()}`;
        }
      }, 500);
    } else {
      toast.error(response.data.error || 'Không thể cập nhật ảnh đại diện');
    }
  } catch (error) {
    console.error('Error updating avatar:', error);
    const errorMessage = error.response?.data?.error || 'Đã xảy ra lỗi khi cập nhật ảnh đại diện';
    toast.error(errorMessage);
  } finally {
    isUpdatingAvatar.value = false;
  }
};
</script>

<template>
  <div class="profile-edit-container">
    <h2 class="text-2xl font-bold mb-6 text-gray-800 pb-2 border-b border-gray-200">Thông tin cá nhân</h2>
    
    <!-- Avatar Section -->
    <div class="mb-8 bg-white p-6 rounded-lg shadow-md">
      <h3 class="text-xl font-semibold mb-4 text-gray-700">Ảnh đại diện</h3>
      
      <div class="flex flex-col md:flex-row items-center gap-6">
        <div class="avatar-container">
          <img 
            :src="avatarUrl" 
            alt="Avatar" 
            class="w-32 h-32 rounded-full object-cover border-4 border-gray-200"
            @error="handleAvatarError"
          />
        </div>
        
        <div class="flex-1">
          <input 
            type="file" 
            id="avatar-upload" 
            accept="image/*" 
            class="hidden" 
            @change="handleAvatarChange"
          />
          
          <div class="flex flex-col gap-3">
            <label 
              for="avatar-upload" 
              class="bg-blue-500 text-white px-4 py-2 rounded-md cursor-pointer hover:bg-blue-600 inline-block text-center w-full md:w-auto"
            >
              Chọn ảnh mới
            </label>
            
            <button 
              @click="updateAvatar" 
              class="bg-green-500 text-white px-4 py-2 rounded-md hover:bg-green-600 w-full md:w-auto"
              :disabled="isUpdatingAvatar || !avatarFile"
              :class="{ 'opacity-70 cursor-not-allowed': isUpdatingAvatar || !avatarFile }"
            >
              <span v-if="isUpdatingAvatar">Đang cập nhật...</span>
              <span v-else>Cập nhật ảnh đại diện</span>
            </button>
          </div>
          
          <p v-if="errors.avatar" class="text-red-500 mt-2 text-sm">{{ errors.avatar }}</p>
          <p v-if="avatarFile" class="text-green-600 mt-2 text-sm">Đã chọn: {{ avatarFile.name }}</p>
        </div>
      </div>
    </div>
    
    <!-- Profile Information Section -->
    <div class="mb-8 bg-white p-6 rounded-lg shadow-md">
      <h3 class="text-xl font-semibold mb-4 text-gray-700">Thông tin tài khoản</h3>
      
      <div class="space-y-4">
        <div>
          <label for="username" class="block text-sm font-medium text-gray-700 mb-1">Tên đăng nhập</label>
          <input 
            type="text" 
            id="username" 
            v-model="usernameInput" 
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            :class="{ 'border-red-500': errors.username }"
          />
          <p v-if="errors.username" class="text-red-500 mt-1 text-sm">{{ errors.username }}</p>
        </div>
        
        <div>
          <label for="fullName" class="block text-sm font-medium text-gray-700 mb-1">Họ và tên</label>
          <input 
            type="text" 
            id="fullName" 
            v-model="fullNameInput" 
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        
        <div>
          <button 
            @click="updateProfile" 
            class="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600"
            :disabled="isUpdatingProfile"
            :class="{ 'opacity-70 cursor-not-allowed': isUpdatingProfile }"
          >
            <span v-if="isUpdatingProfile">Đang cập nhật...</span>
            <span v-else>Cập nhật thông tin</span>
          </button>
        </div>
      </div>
    </div>
    
    <!-- Change Password Section -->
    <div class="mb-8 bg-white p-6 rounded-lg shadow-md">
      <h3 class="text-xl font-semibold mb-4 text-gray-700">Đổi mật khẩu</h3>
      
      <div class="space-y-4">
        <div>
          <label for="currentPassword" class="block text-sm font-medium text-gray-700 mb-1">Mật khẩu hiện tại</label>
          <input 
            type="password" 
            id="currentPassword" 
            v-model="currentPassword" 
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            :class="{ 'border-red-500': errors.currentPassword }"
          />
          <p v-if="errors.currentPassword" class="text-red-500 mt-1 text-sm">{{ errors.currentPassword }}</p>
        </div>
        
        <div>
          <label for="newPassword" class="block text-sm font-medium text-gray-700 mb-1">Mật khẩu mới</label>
          <input 
            type="password" 
            id="newPassword" 
            v-model="newPassword" 
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            :class="{ 'border-red-500': errors.newPassword }"
          />
          <p v-if="errors.newPassword" class="text-red-500 mt-1 text-sm">{{ errors.newPassword }}</p>
        </div>
        
        <div>
          <label for="confirmPassword" class="block text-sm font-medium text-gray-700 mb-1">Xác nhận mật khẩu mới</label>
          <input 
            type="password" 
            id="confirmPassword" 
            v-model="confirmPassword" 
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            :class="{ 'border-red-500': errors.confirmPassword }"
          />
          <p v-if="errors.confirmPassword" class="text-red-500 mt-1 text-sm">{{ errors.confirmPassword }}</p>
        </div>
        
        <div>
          <button 
            @click="updatePassword" 
            class="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600"
            :disabled="isUpdatingPassword"
            :class="{ 'opacity-70 cursor-not-allowed': isUpdatingPassword }"
          >
            <span v-if="isUpdatingPassword">Đang cập nhật...</span>
            <span v-else>Đổi mật khẩu</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.profile-edit-container {
  padding: 20px;
  max-width: 900px;
  margin: 0 auto;
}

.avatar-container {
  position: relative;
  width: 128px;
  height: 128px;
}
</style>
