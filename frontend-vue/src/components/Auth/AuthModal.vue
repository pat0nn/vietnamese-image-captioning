<script setup>
import { ref } from 'vue';
import { useAuthStore } from '../../stores/auth';
import { useToast } from 'vue-toastification';

const props = defineProps({
  onClose: {
    type: Function,
    default: () => {}
  }
});

const emit = defineEmits(['close']);

const authStore = useAuthStore();
const toast = useToast();

const isLogin = ref(true);
const name = ref('');
const username = ref('');
const email = ref('');
const password = ref('');
const error = ref('');
const isLoading = ref(false);

const validateForm = () => {
  if (isLogin.value) {
    if (!username.value || !password.value) {
      error.value = 'Vui lòng nhập tên đăng nhập và mật khẩu';
      return false;
    }
  } else {
    if (!username.value || !password.value || !name.value || !email.value) {
      error.value = 'Vui lòng điền đầy đủ thông tin';
      return false;
    }
  }
  
  return true;
};

const handleSubmit = async () => {
  error.value = '';
  
  if (!validateForm()) {
    return;
  }
  
  isLoading.value = true;
  
  try {
    if (isLogin.value) {
      await authStore.login(username.value, password.value);
      toast.success('Đăng nhập thành công!');
    } else {
      await authStore.register(name.value, username.value, email.value, password.value);
      toast.success('Đăng ký thành công!');
    }
    emit('close');
  } catch (err) {
    error.value = err.response?.data?.message || (isLogin.value ? 'Đăng nhập thất bại' : 'Đăng ký thất bại');
    toast.error(error.value);
  } finally {
    isLoading.value = false;
  }
};

const toggleAuthMode = () => {
  isLogin.value = !isLogin.value;
  error.value = '';
};
</script>

<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg p-8 max-w-md w-full">
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-bold">
          {{ isLogin ? 'Đăng nhập' : 'Đăng ký' }}
        </h2>
        <button 
          @click="emit('close')" 
          class="text-gray-500 hover:text-gray-700"
        >
          &times;
        </button>
      </div>
      
      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div v-if="!isLogin" class="space-y-2">
          <label for="name" class="block text-gray-700">Tên hiển thị</label>
          <input
            id="name"
            v-model="name"
            type="text"
            class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Nhập tên của bạn"
          />
        </div>
        
        <div class="space-y-2">
          <label for="username" class="block text-gray-700">Tên đăng nhập</label>
          <input
            id="username"
            v-model="username"
            type="text"
            class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Nhập tên đăng nhập của bạn"
          />
        </div>
        
        <div v-if="!isLogin" class="space-y-2">
          <label for="email" class="block text-gray-700">Email</label>
          <input
            id="email"
            v-model="email"
            type="email"
            class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Nhập email của bạn"
          />
        </div>
        
        <div class="space-y-2">
          <label for="password" class="block text-gray-700">Mật khẩu</label>
          <input
            id="password"
            v-model="password"
            type="password"
            class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Nhập mật khẩu của bạn"
          />
        </div>
        
        <div v-if="error" class="text-red-500 text-sm">
          {{ error }}
        </div>
        
        <div class="pt-2">
          <button
            type="submit"
            :disabled="isLoading"
            class="w-full py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
            :class="{ 'opacity-70 cursor-not-allowed': isLoading }"
          >
            {{ isLoading ? 'Đang xử lý...' : (isLogin ? 'Đăng nhập' : 'Đăng ký') }}
          </button>
        </div>
      </form>
      
      <div class="mt-4 text-center">
        <button
          @click="toggleAuthMode"
          class="text-blue-500 hover:underline"
        >
          {{ isLogin ? 'Chưa có tài khoản? Đăng ký ngay' : 'Đã có tài khoản? Đăng nhập' }}
        </button>
      </div>
    </div>
  </div>
</template> 