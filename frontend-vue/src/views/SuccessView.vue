<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';

// Import icons
import CheckCircleIcon from '../assets/icons/check-circle.svg';
import ContentCopyIcon from '../assets/icons/content-copy.svg';
import CheckIcon from '../assets/icons/check.svg';

const route = useRoute();
const router = useRouter();
const id = ref(null);
const clientImg = ref(null);
const isCopied = ref(false);

onMounted(() => {
  // Get query parameters
  id.value = route.query.id;
  clientImg.value = route.query.clientImg;
});

const handleCopyLinkClick = () => {
  const linkText = `https://image-uploader-f08q.onrender.com/image/${id.value}`;
  navigator.clipboard.writeText(linkText).then(() => {
    isCopied.value = true;
    setTimeout(() => {
      isCopied.value = false;
    }, 4000);
  });
  
  console.log("Đã sao chép liên kết");
};

const goToHome = () => {
  router.push('/');
};
</script>

<template>
  <main class="container">
    <div class="flex flex-col items-center justify-center min-h-screen p-4">
      <div class="text-green-500 mb-4 w-16 h-16">
        <img :src="CheckCircleIcon" alt="Success" class="w-full h-full" />
      </div>
      
      <h1 class="text-xl font-bold text-gray-800 mb-6">Tải lên thành công!</h1>
      
      <div class="img-container mb-6 overflow-hidden rounded-lg shadow-md max-w-md">
        <img
          v-if="clientImg"
          :src="clientImg"
          alt="Hình ảnh đã tải lên từ thiết bị của bạn"
          class="max-w-full max-h-[500px] object-contain"
        />
      </div>
      
      <div class="copy-link-container flex items-center bg-gray-100 p-2 rounded-lg w-full max-w-md mb-6">
        <p class="mr-2 text-sm truncate flex-1">
          {{ id ? 'Nhấn vào nút bên phải để sao chép đường dẫn đến ảnh của bạn' : 'Đang tải...' }}
        </p>
        <button 
          :class="[
            'flex items-center justify-center w-10 h-10 rounded-md',
            isCopied ? 'bg-green-500 text-white' : 'bg-blue-500 text-white'
          ]"
          @click="handleCopyLinkClick"
        >
          <img v-if="isCopied" :src="CheckIcon" alt="Đã sao chép" class="w-5 h-5" />
          <img v-else :src="ContentCopyIcon" alt="Sao chép" class="w-5 h-5" />
        </button>
      </div>
      
      <button 
        @click="goToHome" 
        class="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
      >
        Quay lại trang chủ
      </button>
    </div>
  </main>
</template>

<style scoped>
.container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.img-container {
  width: 100%;
  max-width: 375px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.copy-link-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #f3f4f6;
  padding: 0.5rem;
  border-radius: 0.5rem;
  width: 100%;
  max-width: 375px;
}
</style> 