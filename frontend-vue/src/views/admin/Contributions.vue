<template>
  <div class="dashboard-card">
    <div class="flex justify-between items-center mb-4">
      <h3 class="text-xl font-bold leading-none text-gray-900 dark:text-white">Các đóng góp của người dùng</h3>
      <button 
        type="button" 
        class="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-4 py-2 dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800"
        @click="showAddModal = true">
        Thêm đóng góp
      </button>
    </div>
    
    <!-- Search and filters -->
    <div class="flex flex-col md:flex-row items-center justify-between space-y-3 md:space-y-0 md:space-x-4 py-4">
      <div class="w-full md:w-1/2">
        <form class="flex items-center" @submit.prevent="handleSearch">
          <label for="simple-search" class="sr-only">Search</label>
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
              placeholder="Tìm kiếm đóng góp" 
              required>
          </div>
        </form>
      </div>
      <div class="w-full md:w-auto flex flex-col md:flex-row space-y-2 md:space-y-0 items-stretch md:items-center justify-end md:space-x-3 flex-shrink-0">
        <div class="flex items-center space-x-3 w-full md:w-auto">
          <button 
            id="statusDropdownButton" 
            @click="toggleStatusDropdown" 
            class="w-full md:w-auto flex items-center justify-center py-2 px-4 text-sm font-medium text-gray-900 focus:outline-none bg-white rounded-lg border border-gray-200 hover:bg-gray-100 hover:text-blue-700 focus:z-10 focus:ring-4 focus:ring-gray-200 dark:focus:ring-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:text-white dark:hover:bg-gray-700" 
            type="button">
            {{ statusFilter ? getStatusInVietnamese(statusFilter) : 'Tất cả' }}
            <svg class="w-2.5 h-2.5 ml-2.5" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 10 6">
                <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m1 1 4 4 4-4"/>
            </svg>
          </button>
          <!-- Dropdown menu -->
          <div v-if="showStatusDropdown" class="z-10 absolute mt-40 bg-white divide-y divide-gray-100 rounded-lg shadow w-44 dark:bg-gray-700 dark:divide-gray-600">
            <ul class="py-2 text-sm text-gray-700 dark:text-gray-200">
              <li>
                <button @click="setStatusFilter(null)" class="block px-4 py-2 w-full text-left hover:bg-gray-100 dark:hover:bg-gray-600 dark:hover:text-white">Tất cả</button>
              </li>
              <li>
                <button @click="setStatusFilter('pending')" class="block px-4 py-2 w-full text-left hover:bg-gray-100 dark:hover:bg-gray-600 dark:hover:text-white">Đang chờ</button>
              </li>
              <li>
                <button @click="setStatusFilter('approved')" class="block px-4 py-2 w-full text-left hover:bg-gray-100 dark:hover:bg-gray-600 dark:hover:text-white">Đã duyệt</button>
              </li>
              <li>
                <button @click="setStatusFilter('rejected')" class="block px-4 py-2 w-full text-left hover:bg-gray-100 dark:hover:bg-gray-600 dark:hover:text-white">Từ chối</button>
              </li>
            </ul>
          </div>
        </div>
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
      <strong class="font-bold">Error!</strong>
      <span class="block sm:inline"> {{ error }}</span>
    </div>
    
    <!-- Empty state -->
    <div v-else-if="contributions.length === 0" class="text-center py-10">
      <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 13h6m-3-3v6m-9 1V7a2 2 0 012-2h14a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2z" />
      </svg>
      <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">Chưa có đóng góp nào</h3>
      <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
        Bắt đầu bằng cách thêm đóng góp mới hoặc thay đổi tiêu chí tìm kiếm.
      </p>
    </div>
    
    <!-- Contributions Grid -->
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6 gap-4 auto-rows-auto">
      <div v-for="contribution in contributions" :key="contribution.contribution_id" class="bg-white rounded-lg border border-gray-200 shadow-md dark:bg-gray-800 dark:border-gray-700">
        <div class="relative">
          <img 
            class="rounded-t-lg h-48 w-full object-cover cursor-pointer" 
            :src="`${apiUrl}/uploads/${contribution.image_path}`" 
            :alt="contribution.user_caption || contribution.ai_caption"
            @click="openImageModal(contribution)">
          <!-- Status badge moved to top-left -->
          <span 
            :class="[
              'absolute top-2 left-2 text-xs font-medium px-2.5 py-0.5 rounded',
              contribution.status === 'approved' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300' :
              contribution.status === 'rejected' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300' :
              'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300'
            ]">
            {{ getStatusInVietnamese(contribution.status) }}
          </span>
          
          <!-- Action menu moved to top-right of the image -->
          <button 
            @click="toggleActionMenu(contribution.contribution_id)"
            data-action-menu
            class="absolute top-2 right-2 inline-flex items-center p-1 text-sm font-medium text-center text-gray-900 bg-white rounded-lg hover:bg-gray-100 focus:ring-4 focus:outline-none dark:text-white focus:ring-gray-50 dark:bg-gray-800 dark:hover:bg-gray-700 dark:focus:ring-gray-600"
          >
            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
              <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z"></path>
            </svg>
          </button>
          
          <!-- Dropdown menu -->
          <div 
            v-if="activeActionMenu === contribution.contribution_id" 
            class="absolute right-2 top-10 z-10 mt-2 w-44 bg-white rounded-md shadow-lg py-1 ring-1 ring-black ring-opacity-5 focus:outline-none dark:bg-gray-700 dark:divide-gray-600"
          >
            <button 
              @click="openEditModal(contribution)"
              class="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-600"
            >
              <svg class="w-4 h-4 mr-2 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 0L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              Cập nhật
            </button>
            <button 
              @click="confirmDelete(contribution)"
              class="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-600"
            >
              <svg class="w-4 h-4 mr-2 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              Xóa
            </button>
          </div>
        </div>
        <div class="p-5 flex flex-col h-[calc(100%-12rem)]">
          <div v-if="contribution.contributor" class="flex items-center mb-3">
            <svg class="w-4 h-4 text-gray-400 mr-1" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
              <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd"></path>
              </svg>
            <span class="text-sm text-gray-600 dark:text-gray-400">{{ contribution.contributor }}</span>
            <span class="text-xs text-gray-500 ml-2" v-if="contribution.created_at">
              {{ formatDate(contribution.created_at) }}
            </span>
          </div>
          
          <h5 class="mb-2 text-lg font-bold tracking-tight text-gray-900 dark:text-white">Mô tả</h5>
          <p class="mb-3 font-normal text-gray-700 dark:text-gray-400 line-clamp-3">{{ contribution.user_caption || 'Không có mô tả' }}</p>
          
          <!-- Add flex-grow to push the buttons to the bottom -->
          <div class="flex-grow"></div>
          
          <!-- Action buttons for pending contributions -->
          <div v-if="isAdmin && contribution.status === 'pending'" class="mt-auto pt-3 flex space-x-2">
            <button 
              @click="reviewContribution(contribution, 'approved')"
              class="w-1/2 inline-flex items-center justify-center px-3 py-2 text-sm font-medium text-center text-white bg-green-600 rounded-lg hover:bg-green-700 focus:ring-4 focus:outline-none focus:ring-green-300 dark:bg-green-500 dark:hover:bg-green-600 dark:focus:ring-green-700">
              Chấp nhận
            </button>
            <button 
              @click="reviewContribution(contribution, 'rejected')"
              class="w-1/2 inline-flex items-center justify-center px-3 py-2 text-sm font-medium text-center text-white bg-red-600 rounded-lg hover:bg-red-700 focus:ring-4 focus:outline-none focus:ring-red-300 dark:bg-red-500 dark:hover:bg-red-600 dark:focus:ring-red-700">
              Từ chối
            </button>
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
              <span class="sr-only">Previous</span>
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
              <span class="sr-only">Next</span>
              <svg class="w-5 h-5" aria-hidden="true" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"></path>
              </svg>
            </button>
          </li>
        </ul>
      </nav>
    </div>
  </div>

  <!-- Edit Modal -->
  <div v-if="showEditModal" class="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
    <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-4 text-center sm:block sm:p-0">
      <!-- Background overlay -->
      <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="showEditModal = false"></div>
      
      <!-- Modal panel -->
      <div class="inline-block align-middle bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all mx-auto my-8 w-full max-w-md sm:max-w-lg dark:bg-gray-800">
        <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4 dark:bg-gray-800">
          <div class="sm:flex sm:items-start">
            <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left w-full">
              <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-white" id="modal-title">
                Chỉnh sửa 
              </h3>
              <div class="mt-4 space-y-4">
                <div>
                  <label for="user-caption" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Mô tả
                  </label>
                  <textarea 
                    id="user-caption" 
                    v-model="currentContribution.user_caption" 
                    rows="3" 
                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white">
                  </textarea>
                </div>
                
                <div>
                  <label for="status" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Trạng thái
                  </label>
                  <select 
                    id="status" 
                    v-model="currentContribution.status" 
                    class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md dark:bg-gray-700 dark:border-gray-600 dark:text-white">
                    <option value="pending">Đang chờ</option>
                    <option value="approved">Đã duyệt</option>
                    <option value="rejected">Từ chối</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse dark:bg-gray-700">
          <button 
            type="button" 
            class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:ml-3 sm:w-auto sm:text-sm"
            @click="handleUpdateContribution">
            Save
          </button>
          <button 
            type="button" 
            class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm dark:bg-gray-600 dark:text-white dark:border-gray-600 dark:hover:bg-gray-700"
            @click="showEditModal = false">
            Cancel
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Delete Confirmation Modal -->
  <div v-if="showDeleteModal" class="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
    <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-4 text-center sm:block sm:p-0">
      <!-- Background overlay -->
      <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="showDeleteModal = false"></div>
      
      <!-- Modal panel -->
      <div class="inline-block align-middle bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all mx-auto my-8 w-full max-w-md sm:max-w-lg dark:bg-gray-800">
        <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4 dark:bg-gray-800">
          <div class="sm:flex sm:items-start">
            <div class="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10">
              <svg class="h-6 w-6 text-red-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
              <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-white" id="modal-title">
                Xóa đóng góp
              </h3>
              <div class="mt-2">
                <p class="text-sm text-gray-500 dark:text-gray-400">
                  Bạn có chắc chắn muốn xóa đóng góp này không? Hành động này không thể hoàn tác.
                </p>
              </div>
            </div>
          </div>
        </div>
        <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse dark:bg-gray-700">
          <button 
            type="button" 
            class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-red-600 text-base font-medium text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 sm:ml-3 sm:w-auto sm:text-sm"
            @click="handleDeleteContribution">
            Xóa
          </button>
          <button 
            type="button" 
            class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm dark:bg-gray-600 dark:text-white dark:border-gray-600 dark:hover:bg-gray-700"
            @click="showDeleteModal = false">
            Hủy bỏ
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Add Contribution Modal -->
  <div v-if="showAddModal" class="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
    <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-4 text-center sm:block sm:p-0">
      <!-- Background overlay -->
      <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="showAddModal = false"></div>
      
      <!-- Modal panel -->
      <div class="inline-block align-middle bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all mx-auto my-8 w-full max-w-md sm:max-w-lg dark:bg-gray-800">
        <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4 dark:bg-gray-800">
          <div class="sm:flex sm:items-start">
            <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left w-full">
              <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-white" id="modal-title">
                Thêm đóng góp mới
              </h3>
              <div class="mt-4 space-y-4">
                <div>
                  <label for="upload-image" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Tải lên hình ảnh
                  </label>
                  <input 
                    type="file" 
                    id="upload-image" 
                    ref="fileInput"
                    accept="image/*"
                    class="mt-1 block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400"
                    @change="handleFileChange">
                  
                  <div v-if="imagePreview" class="mt-3">
                    <img :src="imagePreview" alt="Image preview" class="max-h-40 rounded">
                  </div>
                </div>
                
                <div>
                  <label for="new-caption" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Mô tả
                  </label>
                  <textarea 
                    id="new-caption" 
                    v-model="newContribution.caption" 
                    rows="3" 
                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                    placeholder="Nhập mô tả cho hình ảnh...">
                  </textarea>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse dark:bg-gray-700">
          <button 
            type="button" 
            class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:ml-3 sm:w-auto sm:text-sm"
            @click="handleAddContribution"
            :disabled="!newContribution.file">
            Gửi
          </button>
          <button 
            type="button" 
            class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm dark:bg-gray-600 dark:text-white dark:border-gray-600 dark:hover:bg-gray-700"
            @click="showAddModal = false">
            Hủy bỏ
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Full Size Image Modal -->
  <div 
    v-if="fullSizeImage" 
    class="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50 p-4 animate-fade-in"
    @click="closeImageModal"
  >
    <div 
      class="bg-white rounded-lg max-w-5xl max-h-[90vh] flex flex-col overflow-hidden shadow-xl dark:bg-gray-800"
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
          :src="fullSizeImage ? `${apiUrl}/uploads/${fullSizeImage.image_path}` : ''"
          :alt="fullSizeImage ? (fullSizeImage.user_caption || fullSizeImage.ai_caption || 'Image') : ''"
          class="max-w-full max-h-[70vh] object-contain"
        />
      </div>
      
      <div class="p-6 border-t border-gray-200 dark:border-gray-700">
        <div v-if="fullSizeImage && fullSizeImage.user_caption" class="mb-4">
          <h3 class="text-sm text-gray-600 dark:text-gray-300 mb-1 font-medium">Mô tả:</h3>
          <p class="text-gray-800 dark:text-gray-200 bg-gray-50 dark:bg-gray-700 p-3 rounded border-l-4 border-blue-500">
            {{ fullSizeImage.user_caption }}
          </p>
        </div>
        
        <div v-if="fullSizeImage && fullSizeImage.ai_caption" class="mb-4">
            <h3 class="text-sm text-gray-600 dark:text-gray-300 mb-1 font-medium">Mô tả AI:</h3>
          <p class="text-gray-800 dark:text-gray-200 bg-gray-50 dark:bg-gray-700 p-3 rounded border-l-4 border-green-500">
            {{ fullSizeImage.ai_caption }}
          </p>
        </div>
        
        <div v-if="fullSizeImage" class="flex items-center mt-4">
          <span class="px-2.5 py-0.5 rounded text-xs font-medium mr-2" 
            :class="[
              fullSizeImage.status === 'approved' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300' :
              fullSizeImage.status === 'rejected' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300' :
              'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300'
            ]">
            {{ fullSizeImage.status }}
          </span>
          
          <span v-if="fullSizeImage.contributor" class="text-sm text-gray-600 dark:text-gray-400">
            {{ fullSizeImage.contributor }}
          </span>
          
          <span v-if="fullSizeImage.created_at" class="text-xs text-gray-500 ml-2">
            {{ formatDate(fullSizeImage.created_at) }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../../stores/admin/auth';
import { fetchContributions, updateContribution, deleteContribution, reviewContribution, contributeImage } from '../../utils/adminApi';
import { API_URL } from '../../constants';

export default {
  name: 'ContributionsView',
  setup() {
    const router = useRouter();
    const authStore = useAuthStore();
    const apiUrl = API_URL;
    
    // State
    const contributions = ref([]);
    const loading = ref(false);
    const error = ref(null);
    const searchQuery = ref('');
    const statusFilter = ref(null);
    const showStatusDropdown = ref(false);
    const page = ref(1);
    const limit = ref(10);
    const totalItems = ref(0);
    const showAddModal = ref(false);
    const showEditModal = ref(false);
    const showDeleteModal = ref(false);
    const activeActionMenu = ref(null); // Track which action menu is currently open
    const currentContribution = ref(null);
    const newContribution = ref({
      file: null,
      caption: ''
    });
    const imagePreview = ref(null);
    const fileInput = ref(null);
    const fullSizeImage = ref(null);
    
    // Check if user is admin
    const isAdmin = computed(() => {
      return authStore.user?.is_admin === true;
    });
    
    // Calculate total pages for pagination
    const totalPages = computed(() => {
      return Math.ceil(totalItems.value / limit.value);
    });
    
    // Translate status to Vietnamese
    const getStatusInVietnamese = (status) => {
      switch (status) {
        case 'approved':
          return 'Đã duyệt';
        case 'rejected':
          return 'Đã từ chối';
        case 'pending':
          return 'Chờ duyệt';
        default:
          return status;
      }
    };
    
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
    
    // Fetch contributions based on current filters and pagination
    const loadContributions = async () => {
      loading.value = true;
      error.value = null;
      
      try {
        const response = await fetchContributions({
          page: page.value,
          limit: limit.value,
          search: searchQuery.value || undefined,
          status: statusFilter.value || undefined
        });
        
        if (!response.success) {
          throw new Error(response.error || 'Failed to load contributions');
        }
        
        contributions.value = response.data.contributions;
        totalItems.value = response.data.total;
      } catch (err) {
        console.error('Error loading contributions:', err);
        error.value = err.message || 'Failed to load contributions';
      } finally {
        loading.value = false;
      }
    };
    
    // Handle search submission
    const handleSearch = () => {
      page.value = 1; // Reset to first page when searching
      loadContributions();
    };
    
    // Toggle status dropdown
    const toggleStatusDropdown = () => {
      showStatusDropdown.value = !showStatusDropdown.value;
      // Close action menu if open
      activeActionMenu.value = null;
    };
    
    // Set status filter
    const setStatusFilter = (status) => {
      statusFilter.value = status;
      showStatusDropdown.value = false;
      page.value = 1; // Reset to first page when changing filters
      loadContributions();
    };
    
    // Toggle action menu for a specific contribution
    const toggleActionMenu = (contributionId) => {
      if (activeActionMenu.value === contributionId) {
        // If clicking on the same menu that's already open, close it
        activeActionMenu.value = null;
      } else {
        // Otherwise, open this menu and close any other open menu
        activeActionMenu.value = contributionId;
      }
    };
    
    // Handle clicks outside the action menu to close it
    const handleClickOutside = (event) => {
      // Check if the click is outside any action menu button
      if (activeActionMenu.value !== null && 
          !event.target.closest('[data-action-menu]')) {
        activeActionMenu.value = null;
      }
      
      // Also close status dropdown if open
      if (showStatusDropdown.value && 
          !event.target.closest('#statusDropdownButton')) {
        showStatusDropdown.value = false;
      }
    };
    
    // Add click outside listener
    onMounted(() => {
      document.addEventListener('click', handleClickOutside);
      loadContributions();
    });
    
    // Remove click outside listener
    onBeforeUnmount(() => {
      document.removeEventListener('click', handleClickOutside);
    });
    
    // Change page
    const changePage = (newPage) => {
      if (newPage < 1 || newPage > totalPages.value) {
        return;
      }
      
      page.value = newPage;
      loadContributions();
    };
    
    // Open edit modal for a contribution
    const openEditModal = (contribution) => {
      currentContribution.value = { ...contribution };
      showEditModal.value = true;
    };
    
    // Confirm deletion of a contribution
    const confirmDelete = (contribution) => {
      currentContribution.value = contribution;
      showDeleteModal.value = true;
    };
    
    // Handle contribution status update (approve/reject)
    const handleReviewContribution = async (contribution, status) => {
      loading.value = true;
      error.value = null;
      
      try {
        await reviewContribution(contribution.contribution_id, status);
        // Update the contribution status locally
        const index = contributions.value.findIndex(c => c.contribution_id === contribution.contribution_id);
        if (index !== -1) {
          contributions.value[index].status = status;
        }
      } catch (err) {
        console.error(`Error ${status} contribution:`, err);
        error.value = err.message || `Failed to ${status} contribution`;
      } finally {
        loading.value = false;
      }
    };
    
    // Delete contribution
    const handleDeleteContribution = async () => {
      if (!currentContribution.value) return;
      
      loading.value = true;
      error.value = null;
      
      try {
        await deleteContribution(currentContribution.value.contribution_id);
        // Remove the contribution from the list
        contributions.value = contributions.value.filter(
          c => c.contribution_id !== currentContribution.value.contribution_id
        );
        totalItems.value--;
        showDeleteModal.value = false;
        currentContribution.value = null;
      } catch (err) {
        console.error('Error deleting contribution:', err);
        error.value = err.message || 'Failed to delete contribution';
      } finally {
        loading.value = false;
      }
    };
    
    // Initial data loading
    onMounted(() => {
      loadContributions();
    });
    
    // Watch for changes in search query (debounced)
    let searchTimeout;
    watch(searchQuery, () => {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(() => {
        page.value = 1; // Reset to first page
        loadContributions();
      }, 500); // Debounce search for 500ms
    });
    
    // Update contribution
    const handleUpdateContribution = async () => {
      if (!currentContribution.value) return;
      
      loading.value = true;
      error.value = null;
      
      try {
        await updateContribution(
          currentContribution.value.contribution_id,
          {
            user_caption: currentContribution.value.user_caption,
            ai_caption: currentContribution.value.ai_caption,
            status: currentContribution.value.status
          }
        );
        
        // Update the contribution in the list
        const index = contributions.value.findIndex(
          c => c.contribution_id === currentContribution.value.contribution_id
        );
        
        if (index !== -1) {
          contributions.value[index] = { 
            ...contributions.value[index],
            user_caption: currentContribution.value.user_caption,
            ai_caption: currentContribution.value.ai_caption,
            status: currentContribution.value.status
          };
        }
        
        showEditModal.value = false;
        currentContribution.value = null;
      } catch (err) {
        console.error('Error updating contribution:', err);
        error.value = err.message || 'Failed to update contribution';
      } finally {
        loading.value = false;
      }
    };
    
    // Handle file change
    const handleFileChange = (event) => {
      const file = event.target.files[0];
      if (!file) {
        newContribution.value.file = null;
        imagePreview.value = null;
        return;
      }
      
      newContribution.value.file = file;
      
      // Create image preview
      const reader = new FileReader();
      reader.onload = (e) => {
        imagePreview.value = e.target.result;
      };
      reader.readAsDataURL(file);
    };
    
    // Add new contribution
    const handleAddContribution = async () => {
      if (!newContribution.value.file) {
        error.value = 'Please select an image to upload';
        return;
      }
      
      loading.value = true;
      error.value = null;
      
      try {
        const formData = new FormData();
        formData.append('image', newContribution.value.file);
        formData.append('caption', newContribution.value.caption || '');
        
        await contributeImage(formData);
        
        // Reset form and close modal
        newContribution.value = {
          file: null,
          caption: ''
        };
        imagePreview.value = null;
        showAddModal.value = false;
        
        // Refresh contributions list
        await loadContributions();
      } catch (err) {
        console.error('Error adding contribution:', err);
        error.value = err.message || 'Failed to add contribution';
      } finally {
        loading.value = false;
      }
    };
    
    // Open full size image modal
    const openImageModal = (contribution) => {
      fullSizeImage.value = contribution;
      document.body.style.overflow = 'hidden'; // Prevent scrolling when modal is open
    };
    
    // Close full size image modal
    const closeImageModal = () => {
      fullSizeImage.value = null;
      document.body.style.overflow = ''; // Re-enable scrolling
    };
    
    // Format date
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
    
    return {
      apiUrl,
      contributions,
      loading,
      error,
      searchQuery,
      statusFilter,
      showStatusDropdown,
      activeActionMenu,
      page,
      limit,
      totalItems,
      totalPages,
      paginationRange,
      isAdmin,
      showAddModal,
      showEditModal,
      showDeleteModal,
      currentContribution,
      newContribution,
      imagePreview,
      fileInput,
      fullSizeImage,
      toggleActionMenu,
      openImageModal,
      closeImageModal,
      handleSearch,
      toggleStatusDropdown,
      setStatusFilter,
      changePage,
      openEditModal,
      confirmDelete,
      reviewContribution: handleReviewContribution,
      handleDeleteContribution,
      handleUpdateContribution,
      handleFileChange,
      handleAddContribution,
      getStatusInVietnamese,
      formatDate
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