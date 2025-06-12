<script setup>
import { ref, onMounted, onBeforeUnmount, computed } from 'vue';
import { useAuthStore } from '../../stores/auth';
import { useRouter } from 'vue-router';
import AuthModal from './AuthModal.vue';
import { useAuthStore as useAdminAuthStore } from '../../stores/admin/auth';
import { CONFIG } from '../../constants';
import { API_URL } from '../../constants';

const authStore = useAuthStore();
const adminAuthStore = useAdminAuthStore();
const router = useRouter();
const showAuthModal = ref(false);
const showDropdown = ref(false);
const profileMenuRef = ref(null);
const defaultAvatar = `${API_URL}/uploads/avatars/default.jpg?t=1747130856326`;

// Computed property for avatar URL to match the approach in ProfileEdit.vue
const avatarUrl = computed(() => {
  
  if (authStore.currentUser?.avatar) {
    // If avatar is a full URL (starts with http), use it directly
    if (authStore.currentUser.avatar.startsWith('http')) {
      return authStore.currentUser.avatar;
    } else if (authStore.currentUser.avatar !== 'default.jpg') {
      // Otherwise, construct the full URL
      const url = `${API_URL}/uploads/avatars/${authStore.currentUser.avatar}`;
      return url;
    }
  }
  
  return defaultAvatar;
});

const handleLogout = () => {
  authStore.logout();
  showDropdown.value = false;
};

const goToProfile = () => {
  router.push('/profile');
  showDropdown.value = false;
};

const goToAdmin = async () => {
  showDropdown.value = false;
  
  // Check if already authenticated in admin store
  if (adminAuthStore.isAuthenticated && adminAuthStore.isAdmin) {
    router.push('/admin');
    return;
  }
  
  // Try to authenticate with admin store using current token
  if (authStore.isAuthenticated && authStore.isAdmin) {
    // Get user info from regular auth store
    const userData = authStore.currentUser;
    if (!userData) {
      router.push('/admin/login?redirect=/admin');
      return;
    }
    
    try {
      // Set admin store state using current auth data
      adminAuthStore.token = authStore.token;
      adminAuthStore.user = {
        ...userData,
        is_admin: true // Ensure is_admin flag is set
      };
      
      // Save to localStorage with both keys to support both auth systems
      // Main site uses 'token'
      localStorage.setItem('token', authStore.token);
      // Admin site uses CONFIG.TOKEN_KEY (auth_token)
      localStorage.setItem(CONFIG.TOKEN_KEY, authStore.token);
      localStorage.setItem('user', JSON.stringify(adminAuthStore.user));
      
      // Initialize the admin store to make sure it recognizes the token
      await adminAuthStore.initialize();
      
      // Navigate to admin
      router.push('/admin');
    } catch (error) {
      router.push('/admin/login?redirect=/admin');
    }
  } else {
    // Not authenticated or not admin, redirect to login
    router.push('/admin/login?redirect=/admin');
  }
};

const toggleDropdown = () => {
  showDropdown.value = !showDropdown.value;
};

// Handle clicks outside the dropdown
const handleClickOutside = (event) => {
  if (profileMenuRef.value && !profileMenuRef.value.contains(event.target)) {
    showDropdown.value = false;
  }
};

// Add event listener on mount
onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

// Remove event listener before unmount
onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside);
});

// Get user initials for avatar fallback
const getUserInitials = () => {
  const username = authStore.currentUser?.username || 'Người dùng';
  return username
    .substring(0, 2)
    .toUpperCase();
};
</script>

<template>
  <div class="auth-nav flex items-center">
    <div v-if="authStore.isAuthenticated" ref="profileMenuRef" class="relative">
      <div @click="toggleDropdown" class="flex items-center space-x-3 cursor-pointer select-none">
        <!-- Avatar -->
        <div class="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center overflow-hidden avatar-container">
          <img 
            :src="avatarUrl" 
            :alt="authStore.currentUser?.name || 'Người dùng'"
            class="w-full h-full object-cover"
            @error="$event.target.src = defaultAvatar"
          />
        </div>
        
        <!-- Username -->
        <span class="text-gray-700">{{ authStore.currentUser?.username || 'Người dùng' }}</span>
        
        <!-- Dropdown indicator -->
        <svg 
          xmlns="http://www.w3.org/2000/svg" 
          class="h-4 w-4 text-gray-500" 
          :class="{ 'transform rotate-180': showDropdown }"
          fill="none" 
          viewBox="0 0 24 24" 
          stroke="currentColor"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </div>
      
      <!-- Dropdown Menu -->
      <transition name="dropdown">
        <div v-if="showDropdown" class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-10 border border-gray-200">
          <button 
            @click="goToProfile"
            class="w-full text-left px-4 py-2 text-gray-700 hover:bg-gray-100 flex items-center"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 text-gray-500" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd" />
            </svg>
            Hồ sơ
          </button>
          <!-- Admin Button for admin users -->
          <button 
            v-if="authStore.isAdmin"
            @click="goToAdmin"
            class="w-full text-left px-4 py-2 text-gray-700 hover:bg-gray-100 flex items-center"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 text-gray-500" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M5 3a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2V5a2 2 0 00-2-2H5zm0 2h10v7h-2l-1 2H8l-1-2H5V5z" clip-rule="evenodd" />
            </svg>
            Quản lý
          </button>
          <button 
            @click="handleLogout"
            class="w-full text-left px-4 py-2 text-red-600 hover:bg-gray-100 flex items-center"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 text-red-500" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M3 3a1 1 0 00-1 1v12a1 1 0 001 1h12a1 1 0 001-1V4a1 1 0 00-1-1H3zm-1 9a1 1 0 011-1h6a1 1 0 110 2H3a1 1 0 01-1-1zm10.293-5.707a1 1 0 011.414 0l3 3a1 1 0 010 1.414l-3 3a1 1 0 01-1.414-1.414L14.586 11H7a1 1 0 110-2h7.586l-2.293-2.293a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
            Đăng xuất
          </button>
        </div>
      </transition>
    </div>
    
    <div v-else>
      <button
        @click="showAuthModal = true"
        class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
      >
        Đăng nhập
      </button>
    </div>
    
    <AuthModal 
      v-if="showAuthModal" 
      @close="showAuthModal = false" 
    />
  </div>
</template>

<script>
import AuthModal from './AuthModal.vue';

export default {
  components: {
    AuthModal
  }
}
</script>

<style scoped>
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.2s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Hover effect for the avatar */
.avatar-container:hover {
  filter: brightness(95%);
}
</style> 