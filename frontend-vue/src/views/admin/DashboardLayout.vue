<template>
  <div class="flex flex-col md:flex-row">
    <!-- Sidebar -->
    <aside
      :class="[
        'fixed top-0 left-0 w-64 h-screen pt-16 transition-transform bg-white border-r border-gray-200 md:translate-x-0 dark:bg-gray-800 dark:border-gray-700',
        isSidebarOpen ? 'translate-x-0 z-40' : '-translate-x-full z-40',
        'md:z-30'
      ]"
      aria-label="Sidenav"
      @click.self="closeSidebarIfMobile"
    >
      <div class="overflow-y-auto py-5 px-3 h-full bg-white dark:bg-gray-800">
        <ul class="space-y-2">
          <li>
            <router-link to="/admin" class="sidebar-item" @click="closeSidebarIfMobile">
              <svg class="w-6 h-6 text-gray-500 transition duration-75 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                <path d="M2 10a8 8 0 018-8v8h8a8 8 0 11-16 0z"></path>
                <path d="M12 2.252A8.014 8.014 0 0117.748 8H12V2.252z"></path>
              </svg>
              <span class="ml-3">Trang chủ</span>
            </router-link>
          </li>
          <li>
            <router-link to="/admin/users" class="sidebar-item" @click="closeSidebarIfMobile">
              <svg class="w-6 h-6 text-gray-500 transition duration-75 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                <path d="M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z"></path>
              </svg>
              <span class="ml-3">Người dùng</span>
            </router-link>
          </li>
          <li>
            <router-link to="/admin/contributions" class="sidebar-item" @click="closeSidebarIfMobile">
              <svg class="w-6 h-6 text-gray-500 transition duration-75 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                <path fill-rule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clip-rule="evenodd"></path>
              </svg>
              <span class="ml-3">Đóng góp</span>
            </router-link>
          </li>
          <li>
            <router-link to="/admin/caption-history" class="sidebar-item" @click="closeSidebarIfMobile">
              <svg class="w-6 h-6 text-gray-500 transition duration-75 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clip-rule="evenodd"></path>
              </svg>
              <span class="ml-3">Lịch sử</span>
            </router-link>
          </li>
          <li>
            <router-link to="/admin/download" class="sidebar-item" @click="closeSidebarIfMobile">
              <svg class="w-6 h-6 text-gray-500 transition duration-75 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                <path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd"></path>
              </svg>
              <span class="ml-3">Tải xuống</span>
            </router-link>
          </li>
        </ul>
      </div>
    </aside>

    <div class="md:ml-64 flex-1 flex flex-col min-h-screen bg-gray-50 dark:bg-gray-900">
      <!-- Top Navbar -->
      <nav class="bg-white border-b border-gray-200 px-4 py-2.5 dark:bg-gray-800 dark:border-gray-700 fixed left-0 right-0 top-0 z-50">
        <div class="flex flex-wrap justify-between items-center">
          <div class="flex justify-start items-center flex-grow max-w-[calc(100%-100px)]">
            <button
              @click="toggleSidebar"
              class="p-2 mr-2 text-gray-600 rounded-lg cursor-pointer md:hidden hover:text-gray-900 hover:bg-gray-100 focus:bg-gray-100 dark:focus:bg-gray-700 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-white"
            >
              <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                <path fill-rule="evenodd" d="M3 5a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 10a1 1 0 011-1h6a1 1 0 110 2H4a1 1 0 01-1-1zM3 15a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd"></path>
              </svg>
            </button>
            <router-link to="/" class="flex items-center truncate">
              <span class="self-center text-xl font-semibold whitespace-nowrap truncate dark:text-white">Hệ Thống Chú Thích Hình Ảnh</span>
            </router-link>
          </div>
          <div class="flex items-center">
            <button
              @click="toggleDarkMode"
              type="button"
              class="ml-3 text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-4 focus:ring-gray-200 dark:focus:ring-gray-700 rounded-lg text-sm p-2.5"
            >
              <svg
                v-if="!darkModeStore.isDarkMode"
                class="w-5 h-5"
                fill="currentColor"
                viewBox="0 0 20 20"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z"></path>
              </svg>
              <svg
                v-else
                class="w-5 h-5"
                fill="currentColor"
                viewBox="0 0 20 20"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 100-2v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" fill-rule="evenodd" clip-rule="evenodd"></path>
              </svg>
            </button>
            <button
              type="button"
              class="flex mx-3 text-sm bg-gray-800 rounded-full md:mr-0 focus:ring-4 focus:ring-gray-300 dark:focus:ring-gray-600"
              id="user-menu-button"
              aria-expanded="false"
              @click="toggleUserMenu"
            >
              <span class="sr-only">Mở menu người dùng</span>
              <img class="w-8 h-8 rounded-full bg-gray-200" 
                   :src="avatarUrl" 
                   alt="user photo"
                   @error="$event.target.src = defaultAvatar" />
            </button>
            <!-- Dropdown menu -->
            <div
              v-show="isUserMenuOpen"
              class="absolute top-10 right-4 z-50 my-4 w-56 text-base list-none bg-white rounded divide-y divide-gray-100 shadow dark:bg-gray-700 dark:divide-gray-600"
              id="dropdown"
            >
              <div class="py-3 px-4">
                <span class="block text-sm font-semibold text-gray-900 dark:text-white">{{ authStore.user?.username }}</span>
                <span class="block text-sm text-gray-900 truncate dark:text-white">{{ authStore.user?.email }}</span>
              </div>
              <ul class="py-1 text-gray-700 dark:text-gray-300" aria-labelledby="dropdown">
                <li>
                  <router-link to="/profile" @click="isUserMenuOpen = false" class="block py-2 px-4 text-sm hover:bg-gray-100 dark:hover:bg-gray-600 dark:text-gray-400 dark:hover:text-white">Hồ sơ của tôi</router-link>
                </li>
              </ul>
              <ul class="py-1 text-gray-700 dark:text-gray-300" aria-labelledby="dropdown">
                <li>
                  <a 
                    href="#" 
                    @click.prevent="logout"
                    class="block py-2 px-4 text-sm hover:bg-gray-100 dark:hover:bg-gray-600 dark:hover:text-white"
                  >Đăng xuất</a>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </nav>

      <!-- Page Content -->
      <main class="p-4 pt-20 h-full flex-grow bg-gray-50 dark:bg-gray-900">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onBeforeUnmount, computed } from 'vue';
import { useAuthStore } from '../../stores/admin/auth';
import { useDarkModeStore } from '../../stores/admin/darkMode';
import { API_URL } from '../../constants';

export default {
  name: 'DashboardLayout',
  setup() {
    const authStore = useAuthStore();
    const darkModeStore = useDarkModeStore();
    const defaultAvatar = `${API_URL}/uploads/avatars/default.jpg?t=1747130856326`;
    
    const isSidebarOpen = ref(window.innerWidth >= 768);
    const isUserMenuOpen = ref(false);
    
    const toggleSidebar = () => {
      isSidebarOpen.value = !isSidebarOpen.value;
    };
    
    const closeSidebarIfMobile = () => {
      // Close sidebar on mobile when clicking a menu item
      if (window.innerWidth < 768) {
        isSidebarOpen.value = false;
      }
    };
    
    const toggleUserMenu = () => {
      isUserMenuOpen.value = !isUserMenuOpen.value;
    };
    
    const toggleDarkMode = () => {
      darkModeStore.toggle();
    };
    
    const logout = () => {
      // Close the dropdown
      isUserMenuOpen.value = false;
      
      // Log for debugging
      console.log('Logging out from admin dashboard');
      
      // Call the logout method from auth store
      authStore.logout();
      
      // Note: No need to manually redirect here as the store's logout method will handle it
      console.log('Logout complete, redirecting to home page');
    };
    
    const handleClickOutside = (event) => {
      const userMenuElement = document.getElementById('user-menu');
      if (userMenuElement && !userMenuElement.contains(event.target) && !event.target.closest('#user-menu-button')) {
        isUserMenuOpen.value = false;
      }
    };
    
    // Xử lý khi kích thước màn hình thay đổi
    const handleResize = () => {
      // Tự động mở sidebar trên màn hình lớn, đóng trên màn hình nhỏ
      if (window.innerWidth >= 768) {
        isSidebarOpen.value = true;
      } else {
        isSidebarOpen.value = false;
      }
    };
    
    // Computed property for avatar URL
    const avatarUrl = computed(() => {
      console.log('Admin user data:', authStore.user);
      console.log('Admin avatar value:', authStore.user?.avatar);
      
      if (authStore.user?.avatar) {
        // If avatar is a full URL (starts with http), use it directly
        if (authStore.user.avatar.startsWith('http')) {
          console.log('Using HTTP avatar URL in admin');
          return authStore.user.avatar;
        } else if (authStore.user.avatar !== 'default.jpg') {
          // Otherwise, construct the full URL
          const url = `${API_URL}/uploads/avatars/${authStore.user.avatar}`;
          console.log('Generated avatar URL in admin:', url);
          return url;
        }
      }
      
      console.log('Using default avatar in admin');
      return defaultAvatar;
    });
    
    onMounted(async () => {
      document.addEventListener('click', handleClickOutside);
      window.addEventListener('resize', handleResize);
      darkModeStore.initialize();
      
      // Initialize the auth store to ensure user data is loaded
      console.log('DashboardLayout mounted, initializing auth store');
      await authStore.initialize();
      console.log('Auth store initialized, user:', authStore.user);
    });
    
    onBeforeUnmount(() => {
      document.removeEventListener('click', handleClickOutside);
      window.removeEventListener('resize', handleResize);
    });
    
    return {
      authStore,
      darkModeStore,
      isSidebarOpen,
      isUserMenuOpen,
      toggleSidebar,
      closeSidebarIfMobile,
      toggleUserMenu,
      toggleDarkMode,
      logout,
      handleResize,
      defaultAvatar,
      avatarUrl
    };
  }
}
</script>

<style>
/* Sidebar item styling */
.sidebar-item {
  display: flex;
  align-items: center;
  padding: 0.5rem;
  text-decoration: none;
  font-size: 1rem;
  color: #374151;
  border-radius: 0.375rem;
}

.sidebar-item:hover {
  background-color: #f3f4f6;
}

.dark .sidebar-item {
  color: #fff;
}

.dark .sidebar-item:hover {
  background-color: #374151;
}

/* Fix for mobile layout issues */
@media (max-width: 768px) {
  .sidebar-item {
    padding-right: 1rem;
  }
  
  /* Ensure header content doesn't overflow */
  nav .flex-grow {
    min-width: 0;
  }
  
  /* Improve title truncation on small screens */
  nav .truncate {
    max-width: 200px;
  }
  
  /* Ensure sidebar stays below header */
  aside {
    z-index: 40 !important;
    padding-top: 56px !important; /* header height */
  }
  
  /* Ensure dropdown menus are visible above sidebar */
  #dropdown {
    z-index: 70 !important;
  }
  
  nav {
    z-index: 50 !important;
  }
}
</style> 