<template>
  <div class="dashboard-card dark:bg-gray-800">
    <div class="flex justify-between items-center mb-4">
      <h3 class="text-xl font-bold leading-none text-gray-900 dark:text-white">Người dùng</h3>
      <button @click="showAddUserModal = true" type="button" class="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-4 py-2 dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800">
        Thêm người dùng
      </button>
    </div>
    
    <!-- Loading state -->
    <div v-if="loading" class="flex justify-center items-center py-10">
      <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-700"></div>
    </div>
    
    <!-- Error state -->
    <div v-else-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative my-4" role="alert">
      <strong class="font-bold">Lỗi!</strong>
      <span class="block sm:inline"> {{ error }}</span>
    </div>
    
    <!-- Content when loaded -->
    <div v-else>
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
              <input v-model="searchQuery" type="text" id="simple-search" class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full pl-10 p-2 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500" placeholder="Tìm kiếm người dùng" required>
            </div>
            <button type="submit" class="p-2.5 ml-2 text-sm font-medium text-white bg-blue-700 rounded-lg border border-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
              <span class="sr-only">Tìm kiếm</span>
            </button>
          </form>
        </div>
      </div>
      
      <!-- No users found -->
      <div v-if="users.length === 0" class="text-center py-10">
        <p class="text-gray-500 dark:text-gray-400">Không tìm thấy người dùng</p>
      </div>
      
      <!-- Users table -->
      <div v-else class="overflow-x-auto relative shadow-md sm:rounded-lg">
        <table class="w-full text-sm text-left text-gray-500 dark:text-gray-400">
          <thead class="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400">
            <tr>
              <th scope="col" class="px-6 py-3">Tên/Email</th>
              <th scope="col" class="px-6 py-3">Quản trị viên</th>
              <th scope="col" class="px-6 py-3 text-right">
                <span class="sr-only">Hành động</span>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.id" class="bg-white border-b dark:bg-gray-800 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600">
              <th scope="row" class="flex items-center px-6 py-4 text-gray-900 whitespace-nowrap dark:text-white">
                <img 
                  class="w-10 h-10 rounded-full bg-gray-200" 
                  :src="getAvatarUrl(user.avatar)" 
                  :alt="`${user.username || 'User'} avatar`"
                  @error="$event.target.src = defaultAvatar"
                >
                <div class="pl-3">
                  <div class="text-base font-semibold">{{ user.full_name || user.username }}</div>
                  <div class="font-normal text-gray-500">{{ user.email }}</div>
                </div>  
              </th>
              <td class="px-6 py-4">
                <div class="flex items-center">
                  <div :class="[
                    'h-2.5 w-2.5 rounded-full mr-2',
                    user.is_admin ? 'bg-blue-500' : 'bg-gray-300'
                  ]"></div>
                  {{ user.is_admin ? 'Có' : 'Không' }}
                </div>
              </td>
              <td class="px-6 py-4">
                <div class="flex justify-end space-x-4">
                  <button @click="editUser(user)" type="button" class="flex items-center font-medium text-blue-600 dark:text-blue-500 hover:underline">
                    <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 0L11.828 15H9v-2.828l8.586-8.586z"></path>
                    </svg>
                    <span class="hidden md:inline">Sửa</span>
                  </button>
                  <button @click="confirmDelete(user)" type="button" class="flex items-center font-medium text-red-600 dark:text-red-500 hover:underline">
                    <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                    </svg>
                    <span class="hidden md:inline">Xóa</span>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- Pagination -->
      <nav v-if="pagination.total_pages > 1" class="flex flex-col md:flex-row justify-between items-start md:items-center space-y-3 md:space-y-0 p-4" aria-label="Table navigation">
        <span class="text-sm font-normal text-gray-500 dark:text-gray-400">
          Hiển thị <span class="font-semibold text-gray-900 dark:text-white">{{ (pagination.page - 1) * pagination.limit + 1 }}-{{ Math.min(pagination.page * pagination.limit, pagination.total) }}</span> trên <span class="font-semibold text-gray-900 dark:text-white">{{ pagination.total }}</span>
        </span>
        <ul class="inline-flex items-stretch -space-x-px">
          <li>
            <button 
              @click="changePage(pagination.page - 1)" 
              :disabled="pagination.page <= 1"
              :class="{'opacity-50 cursor-not-allowed': pagination.page <= 1}"
              class="flex items-center justify-center h-full py-1.5 px-3 ml-0 text-gray-500 bg-white rounded-l-lg border border-gray-300 hover:bg-gray-100 hover:text-gray-700 dark:bg-gray-800 dark:border-gray-700 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-white">
              <span class="sr-only">Trang trước</span>
              <svg class="w-5 h-5" aria-hidden="true" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd"></path>
              </svg>
            </button>
          </li>
          <li v-for="pageNum in paginationRange" :key="pageNum">
            <button 
              @click="changePage(pageNum)" 
              :class="pageNum === pagination.page ? 'text-blue-600 bg-blue-50 border-blue-300 hover:bg-blue-100 hover:text-blue-700 dark:border-gray-700 dark:bg-gray-700 dark:text-white' : 'text-gray-500 bg-white border-gray-300 hover:bg-gray-100 hover:text-gray-700 dark:bg-gray-800 dark:border-gray-700 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-white'"
              class="flex items-center justify-center text-sm py-2 px-3 leading-tight border">
              {{ pageNum }}
            </button>
          </li>
          <li>
            <button 
              @click="changePage(pagination.page + 1)" 
              :disabled="pagination.page >= pagination.total_pages"
              :class="{'opacity-50 cursor-not-allowed': pagination.page >= pagination.total_pages}"
              class="flex items-center justify-center h-full py-1.5 px-3 leading-tight text-gray-500 bg-white rounded-r-lg border border-gray-300 hover:bg-gray-100 hover:text-gray-700 dark:bg-gray-800 dark:border-gray-700 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-white">
              <span class="sr-only">Trang sau</span>
              <svg class="w-5 h-5" aria-hidden="true" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"></path>
              </svg>
            </button>
          </li>
        </ul>
      </nav>
    </div>
    
    <!-- Add/Edit User Modal -->
    <div v-if="showAddUserModal || showEditUserModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-md">
        <div class="p-6">
          <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            {{ showEditUserModal ? 'Chỉnh sửa người dùng' : 'Thêm người dùng mới' }}
          </h3>
          
          <!-- Error message -->
          <div v-if="formError" class="mb-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
            <span class="block sm:inline">{{ formError }}</span>
          </div>
          
          <form @submit.prevent="showEditUserModal ? updateUserData() : createUserData()">
            <div class="grid gap-4 mb-4 sm:grid-cols-2">
              <div class="sm:col-span-2">
                <label for="username" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">Tên đăng nhập</label>
                <input v-model="formData.username" type="text" name="username" id="username" class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-600 focus:border-blue-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500" placeholder="Tên đăng nhập" required>
              </div>
              <div class="sm:col-span-2">
                <label for="email" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">Email</label>
                <input v-model="formData.email" type="email" name="email" id="email" class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-600 focus:border-blue-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500" placeholder="Email" required>
              </div>
              <div class="sm:col-span-2">
                <label for="full_name" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">Họ và tên</label>
                <input v-model="formData.full_name" type="text" name="full_name" id="full_name" class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-600 focus:border-blue-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500" placeholder="Họ và tên">
              </div>
              <div v-if="!showEditUserModal" class="sm:col-span-2">
                <label for="password" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">Mật khẩu</label>
                <input v-model="formData.password" type="password" name="password" id="password" class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-600 focus:border-blue-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500" placeholder="Mật khẩu" :required="!showEditUserModal">
              </div>
              <div v-else class="sm:col-span-2">
                <label for="password" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">Mật khẩu (để trống nếu không thay đổi)</label>
                <input v-model="formData.password" type="password" name="password" id="password" class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-600 focus:border-blue-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500" placeholder="Mật khẩu mới">
              </div>
              <div class="sm:col-span-2">
                <label for="is_admin" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">Quản trị viên</label>
                <select v-model="formData.is_admin" id="is_admin" class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
                  <option :value="false">Không</option>
                  <option :value="true">Có</option>
                </select>
              </div>
              <div class="sm:col-span-2">
                <label for="biography" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">Giới thiệu</label>
                <textarea v-model="formData.biography" id="biography" rows="4" class="block p-2.5 w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500" placeholder="Giới thiệu về người dùng"></textarea>
              </div>
            </div>
            <div class="flex items-center space-x-4">
              <button type="submit" class="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">
                {{ showEditUserModal ? 'Lưu thay đổi' : 'Thêm người dùng' }}
              </button>
              <button type="button" @click="closeModal" class="text-gray-500 bg-white hover:bg-gray-100 focus:ring-4 focus:outline-none focus:ring-blue-300 rounded-lg border border-gray-200 text-sm font-medium px-5 py-2.5 hover:text-gray-900 focus:z-10 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-500 dark:hover:text-white dark:hover:bg-gray-600 dark:focus:ring-gray-600">
                Hủy bỏ
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
    
    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-md">
        <div class="p-6">
          <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">Xác nhận xóa</h3>
          <p class="text-gray-700 dark:text-gray-300 mb-4">
            Bạn có chắc chắn muốn xóa người dùng "{{ userToDelete?.full_name || userToDelete?.username }}"? Hành động này không thể hoàn tác.
          </p>
          <div class="flex justify-end space-x-4">
            <button @click="deleteUserData" type="button" class="text-white bg-red-700 hover:bg-red-800 focus:ring-4 focus:outline-none focus:ring-red-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center dark:bg-red-600 dark:hover:bg-red-700 dark:focus:ring-red-800">
              Xóa
            </button>
            <button @click="showDeleteModal = false" type="button" class="text-gray-500 bg-white hover:bg-gray-100 focus:ring-4 focus:outline-none focus:ring-blue-300 rounded-lg border border-gray-200 text-sm font-medium px-5 py-2.5 hover:text-gray-900 focus:z-10 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-500 dark:hover:text-white dark:hover:bg-gray-600 dark:focus:ring-gray-600">
              Hủy bỏ
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue';
import { fetchUsers, createUser, updateUser, deleteUser } from '../../utils/adminApi';
import { API_URL } from '../../constants';
export default {
  name: 'Users',
  setup() {
    const users = ref([]);
    const loading = ref(true);
    const error = ref(null);
    const defaultAvatar = `${API_URL}/uploads/avatars/default.jpg?t=1747130856326`;
    
    // Pagination
    const pagination = ref({
      page: 1,
      limit: 10,
      total: 0,
      total_pages: 1
    });
    
    // Search
    const searchQuery = ref('');
    
    // Modals
    const showAddUserModal = ref(false);
    const showEditUserModal = ref(false);
    const showDeleteModal = ref(false);
    
    // Form data
    const formData = ref({
      username: '',
      email: '',
      password: '',
      full_name: '',
      biography: '',
      is_admin: false
    });
    const formError = ref('');
    
    // Delete
    const userToDelete = ref(null);

    const paginationRange = computed(() => {
      const range = [];
      const maxVisible = 5;
      const { page, total_pages } = pagination.value;
      
      // Calculate the start and end of the pagination range
      let start = Math.max(1, page - Math.floor(maxVisible / 2));
      let end = Math.min(total_pages, start + maxVisible - 1);
      
      // Adjust the start if we're near the end
      if (end === total_pages) {
        start = Math.max(1, end - maxVisible + 1);
      }
      
      // Generate the range
      for (let i = start; i <= end; i++) {
        range.push(i);
      }
      
      return range;
    });

    const loadUsers = async (page = 1, search = '') => {
      loading.value = true;
      error.value = null;
      
      try {
        const response = await fetchUsers(page, pagination.value.limit, search);
        
        if (response && response.success) {
          users.value = response.users;
          pagination.value = {
            page: response.pagination.page,
            limit: response.pagination.limit,
            total: response.pagination.total,
            total_pages: response.pagination.total_pages
          };
        } else {
          error.value = 'Failed to load users';
        }
      } catch (error) {
        error.value = error.message || 'An unexpected error occurred';
      } finally {
        loading.value = false;
      }
    };
    
    const changePage = async (newPage) => {
      if (newPage < 1 || newPage > pagination.value.total_pages) {
        return;
      }
      
      await loadUsers(newPage, searchQuery.value);
    };
    
    const handleSearch = async () => {
      await loadUsers(1, searchQuery.value);
    };
    
    const resetForm = () => {
      formData.value = {
        username: '',
        email: '',
        password: '',
        full_name: '',
        biography: '',
        is_admin: false
      };
      formError.value = '';
    };
    
    const editUser = (user) => {
      resetForm();
      
      // Copy user data to form
      formData.value = {
        id: user.id,
        username: user.username,
        email: user.email,
        password: '', // Don't set password
        full_name: user.full_name || '',
        biography: user.biography || '',
        is_admin: user.is_admin || false
      };
      
      showEditUserModal.value = true;
    };
    
    const createUserData = async () => {
      formError.value = '';
      
      try {
        const response = await createUser(formData.value);
        
        if (response && response.success) {
          closeModal();
          await loadUsers(pagination.value.page, searchQuery.value);
        } else {
          formError.value = 'Failed to create user';
        }
      } catch (error) {
        formError.value = error.message || 'An unexpected error occurred';
      }
    };
    
    const updateUserData = async () => {
      formError.value = '';
      
      try {
        // Remove empty password if not changed
        const userData = { ...formData.value };
        if (!userData.password) {
          delete userData.password;
        }
        
        const response = await updateUser(userData.id, userData);
        
        if (response && response.success) {
          closeModal();
          await loadUsers(pagination.value.page, searchQuery.value);
        } else {
          formError.value = 'Failed to update user';
        }
      } catch (error) {
        formError.value = error.message || 'An unexpected error occurred';
      }
    };
    
    const confirmDelete = (user) => {
      userToDelete.value = user;
      showDeleteModal.value = true;
    };
    
    const deleteUserData = async () => {
      try {
        if (!userToDelete.value) return;
        
        const response = await deleteUser(userToDelete.value.id);
        
        if (response && response.success) {
          showDeleteModal.value = false;
          userToDelete.value = null;
          await loadUsers(pagination.value.page, searchQuery.value);
        } else {
          error.value = 'Failed to delete user';
        }
      } catch (error) {
        error.value = error.message || 'An unexpected error occurred';
      }
    };
    
    const closeModal = () => {
      showAddUserModal.value = false;
      showEditUserModal.value = false;
      resetForm();
    };

    // Construct proper avatar URL
    const getAvatarUrl = (avatar) => {
      // If no avatar or it's the default, use the default avatar
      if (!avatar || avatar === 'default.jpg') {
        return defaultAvatar;
      }
      
      // If it's already a full URL, use it directly
      if (avatar.startsWith('http')) {
        return avatar;
      }
      
      // Otherwise, construct the full URL to the avatar
      const apiUrl = import.meta.env.VITE_API_URL || API_URL;
      
      // Check if the avatar path already includes 'avatars/'
      if (avatar.startsWith('avatars/')) {
        return `${apiUrl}/uploads/${avatar}`;
      } else {
        return `${apiUrl}/uploads/avatars/${avatar}`;
      }
    };

    onMounted(async () => {
      await loadUsers();
    });

    return {
      users,
      loading,
      error,
      pagination,
      searchQuery,
      showAddUserModal,
      showEditUserModal,
      showDeleteModal,
      formData,
      formError,
      userToDelete,
      paginationRange,
      loadUsers,
      changePage,
      handleSearch,
      resetForm,
      editUser,
      createUserData,
      updateUserData,
      confirmDelete,
      deleteUserData,
      closeModal,
      defaultAvatar,
      getAvatarUrl
    };
  }
}
</script> 