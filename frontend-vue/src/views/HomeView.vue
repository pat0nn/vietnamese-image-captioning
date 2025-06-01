<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue';
import { useToast } from 'vue-toastification';
import { useAuthStore } from '../stores/auth';
import AuthNav from '../components/Auth/AuthNav.vue';
import AuthModal from '../components/Auth/AuthModal.vue';
import RatingStars from '../components/RatingStars.vue';
import { getImageCaption, contributeImage, submitRating, textToSpeech } from '../utils/requestHelper';
import { playAudioFromBase64, stopAudio } from '../utils/audioHelper';
import { useRouter } from 'vue-router';

// Images
import mainImage from '@/assets/image.svg';

// Component state
const fileInputRef = ref(null);
const cameraInputRef = ref(null);
const dropzone = ref(null);
const zoneImage = ref(null);
const zoneText = ref(null);
const audioRef = ref(null);

const clientError = ref('');
const dragging = ref(false);
const previewImage = ref(null);
const isLoading = ref(false);
const imageCaption = ref('');
const userCaption = ref('');
const isSaving = ref(false);
const isContributing = ref(false);
const contributionSuccess = ref(false);
const selectedFile = ref(null);
const showAuthModal = ref(false);
const isPlaying = ref(false);
const audioData = ref(null);
const isCameraSupported = ref(false);
const autoPlayError = ref(false);
const currentImageId = ref(null);

const authStore = useAuthStore();
const toast = useToast();
const router = useRouter();

// Create a reference to the active controller for cancellation
const abortController = ref(null);

// Check if camera is supported
onMounted(() => {
  // Most mobile devices support capture
  isCameraSupported.value = true;
});

// Clean up audio on component unmount
onBeforeUnmount(() => {
  if (audioRef.value) {
    stopAudio(audioRef.value);
    audioRef.value = null;
  }
});

// Drag and drop handlers
const handleDragOver = (e) => {
  e.preventDefault();
  e.stopPropagation();
};

const handleDrop = (e) => {
  e.preventDefault();
  e.stopPropagation();
  dragging.value = false;
  const files = e.dataTransfer.files;
  if (files && files.length === 1) {
    handleAddFile(files);
    return;
  }
  clientError.value = "Chỉ có thể tải lên một tệp. Vui lòng tải lên một hình ảnh duy nhất.";
};

const handleDragEnter = (e) => {
  if (e.target === zoneImage.value || e.target === zoneText.value) return;
  e.preventDefault();
  e.stopPropagation();
  dragging.value = true;
};

const handleDragLeave = (e) => {
  if (e.target === zoneImage.value || e.target === zoneText.value) return;
  e.preventDefault();
  e.stopPropagation();
  dragging.value = false;
};

// File handling functions
const handleAddFile = async (fileList) => {
  const imageFile = fileList[0];

  if (!imageFile) {
    clientError.value = "Vui lòng tải lên một hình ảnh.";
    return;
  }

  if (!imageFile.type.startsWith("image/")) {
    clientError.value = "Chỉ có thể tải lên tệp hình ảnh. Vui lòng tải lên tệp hợp lệ.";
    return;
  }

  selectedFile.value = imageFile;
  const imgURL = URL.createObjectURL(imageFile);
  previewImage.value = imgURL;
  clientError.value = "";
  contributionSuccess.value = false;
  currentImageId.value = null;

  // Get caption if not in contribution mode
  if (!isContributing.value) {
    await uploadAndGetCaption(imageFile);
  }
};

// Open camera
const openCamera = () => {
  if (cameraInputRef.value) {
    cameraInputRef.value.click();
  }
};

// Upload image and get caption
const uploadAndGetCaption = async (imageFile) => {
  // Tạo một biến nội bộ để theo dõi trạng thái hủy
  let wasCanceled = false;
  
  // Cancel any existing request
  if (abortController.value) {
    abortController.value.abort();
  }
  
  // Create a new abort controller for this request
  abortController.value = new AbortController();
  
  // Monitor the abort signal
  abortController.value.signal.addEventListener('abort', () => {
    wasCanceled = true;
  });
  
  // Set loading state and clear old data
  isLoading.value = true;
  imageCaption.value = "";
  audioData.value = null;
  autoPlayError.value = false;
  currentImageId.value = null;
  clientError.value = ""; // Xóa lỗi hiện tại khi bắt đầu request mới
  
  // Stop any playing audio
  if (isPlaying.value && audioRef.value) {
    isPlaying.value = false;
    stopAudio(audioRef.value);
    audioRef.value = null;
  }
  
  try {
    const formData = new FormData();
    formData.append('image', imageFile);
    // Request audio generation with the caption
    formData.append('generateAudio', 'true');
    
    const data = await getImageCaption(formData, abortController.value.signal);
    
    // Nếu request đã bị hủy, không làm gì cả
    if (wasCanceled) return;
    
    // Save image_id for rating
    if (data.image_id) {
      currentImageId.value = data.image_id;
    }
    
    // Check if response has both caption and audio
    if (data.caption && data.audio) {
      console.log("Received both caption and audio data");
      
      // Save audio data
      audioData.value = data.audio;
      
      // Play audio immediately
      const audio = playAudioFromBase64(
        data.audio,
        () => {
          // Callback when audio starts playing
          isPlaying.value = true;
          // Only display caption when audio starts playing
          imageCaption.value = data.caption;
          console.log("Audio playing, caption displayed");
        },
        () => {
          // Callback when audio ends
          isPlaying.value = false;
          audioRef.value = null;
        },
        (error) => {
          // Callback on error
          console.error('Audio playback error:', error);
          isPlaying.value = false;
          audioRef.value = null;
          autoPlayError.value = true;
          
          // Still display caption if audio fails
          if (!imageCaption.value) {
            imageCaption.value = data.caption;
            console.log("Audio failed to play, but caption is displayed");
          }
        }
      );
      audioRef.value = audio;
    } else {
      // If no audio, still display caption if available
      if (data.caption) {
        imageCaption.value = data.caption;
        console.log("No audio data, but caption is displayed");
      } else {
        throw new Error('Không nhận được caption hoặc âm thanh từ máy chủ');
      }
    }
  } catch (error) {
    // Don't show error if it was intentionally aborted
    if (error.name === 'AbortError' || wasCanceled) {
      // Không làm gì cả khi request bị hủy có chủ đích
      return;
    }
    
    console.error('Error getting caption:', error);
    clientError.value = error.message || 'Không thể nhận mô tả hình ảnh';
    toast.error('Không thể tạo mô tả hình ảnh', { timeout: 3000 });
  } finally {
    // Nếu request bị hủy, không cập nhật UI
    if (!wasCanceled) {
      isLoading.value = false;
    }
    abortController.value = null;
  }
};

// Play caption as speech
const playCaption = async () => {
  try {
    // If playing, stop current audio
    if (isPlaying.value && audioRef.value) {
      isPlaying.value = false;
      stopAudio(audioRef.value);
      audioRef.value = null;
      return;
    }
    
    // Mark as playing
    isPlaying.value = true;
    
    // If audio data exists, use it
    if (audioData.value) {
      const audio = playAudioFromBase64(
        audioData.value,
        null, // No onStart callback needed as isPlaying is already set above
        () => {
          isPlaying.value = false;
          audioRef.value = null;
        },
        (error) => {
          console.error('Audio playback error:', error);
          isPlaying.value = false;
          audioRef.value = null;
          // Only show toast when really needed
          if (!error.message?.includes('interrupted') && !error.message?.includes('aborted')) {
            toast.error('Không thể phát giọng nói', { timeout: 2000 });
          }
        }
      );
      audioRef.value = audio;
    } 
    // If not, request from server
    else if (imageCaption.value) {
      try {
        const response = await textToSpeech(imageCaption.value);
        if (response?.audio) {
          audioData.value = response.audio;
          // Only play if still in isPlaying state
          // (user might have pressed stop while waiting for response)
          if (isPlaying.value) {
            const audio = playAudioFromBase64(
              response.audio,
              null,
              () => {
                isPlaying.value = false;
                audioRef.value = null;
              },
              (error) => {
                console.error('Audio playback error:', error);
                isPlaying.value = false;
                audioRef.value = null;
                // Only show toast when really needed
                if (!error.message?.includes('interrupted') && !error.message?.includes('aborted')) {
                  toast.error('Không thể phát giọng nói', { timeout: 2000 });
                }
              }
            );
            audioRef.value = audio;
          }
        } else {
          throw new Error('Không nhận được dữ liệu âm thanh từ máy chủ');
        }
      } catch (error) {
        console.error('Error fetching speech:', error);
        isPlaying.value = false;
        toast.error('Không thể tạo giọng nói', { timeout: 2000 });
      }
    } else {
      isPlaying.value = false;
      toast.info('Không có nội dung để phát', { timeout: 2000 });
    }
  } catch (error) {
    console.error('Error in playCaption:', error);
    isPlaying.value = false;
    audioRef.value = null;
    toast.error('Đã xảy ra lỗi khi phát âm thanh', { timeout: 2000 });
  }
};

// Toggle between AI caption and user contribution modes
const toggleContributionMode = () => {
  if (isContributing.value) {
    // Switch from contribution to AI caption mode
    isContributing.value = false;
    userCaption.value = "";
    contributionSuccess.value = false;
    
    // If an image is selected, get caption for it
    if (selectedFile.value) {
      uploadAndGetCaption(selectedFile.value);
    }
  } else {
    // Switch to contribution mode
    if (!authStore.isAuthenticated) {
      // Show login modal if not authenticated
      showAuthModal.value = true;
      return;
    }
    
    // Cancel any ongoing caption requests
    if (abortController.value) {
      abortController.value.abort();
      abortController.value = null;
    }
    
    // Reset all states khi chuyển sang chế độ đóng góp
    isLoading.value = false;
    clientError.value = ""; // Xóa thông báo lỗi nếu có
    imageCaption.value = ""; // Xóa caption AI hiện tại nếu có
    
    // Stop audio if playing
    if (isPlaying.value && audioRef.value) {
      isPlaying.value = false;
      stopAudio(audioRef.value);
      audioRef.value = null;
    }
    
    isContributing.value = true;
  }
};

// Validate user caption
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

// Save user contribution
const handleSaveContribution = async () => {
  if (!selectedFile.value) {
    clientError.value = "Vui lòng tải lên hình ảnh trước.";
    return;
  }

  // Validate caption
  const validationResult = validateCaption(userCaption.value);
  if (!validationResult.isValid) {
    clientError.value = validationResult.error;
    return;
  }

  // Check authentication
  if (!authStore.isAuthenticated) {
    showAuthModal.value = true;
    return;
  }

  isSaving.value = true;
  clientError.value = "";

  try {
    const formData = new FormData();
    formData.append('image', selectedFile.value);
    formData.append('userCaption', userCaption.value);
    formData.append('skipAiCaption', 'true');

    const response = await contributeImage(formData);

    // Hiển thị thông báo thành công
    contributionSuccess.value = true;
    userCaption.value = "";
    // Reset lại hình ảnh nhưng vẫn giữ chế độ đóng góp
    previewImage.value = null;
    selectedFile.value = null;
    toast.success("Đóng góp của bạn đã được lưu thành công!");
  } catch (error) {
    console.error('Error saving contribution:', error);
    clientError.value = error.response?.data?.error || 'Không thể lưu đóng góp';
    toast.error("Có lỗi xảy ra khi lưu đóng góp của bạn.");
  } finally {
    isSaving.value = false;
  }
};

// Click the file input
const clickFileInput = () => {
  fileInputRef.value.click();
};

// Handle after rating submitted
const handleRatingSubmitted = (rating) => {
  toast.success(`Cảm ơn bạn đã đánh giá ${rating} sao!`, { timeout: 2000 });
};
</script>

<template>
  <div>
    <!-- Navigation Bar -->
    <div class="bg-white shadow-md px-6 py-4 flex justify-between items-center">
      <router-link to="/">
        <h1 class="text-xl font-bold text-blue-500">Hệ Thống Mô Tả Hình Ảnh</h1>
      </router-link>
      <AuthNav />
    </div>
    
    <!-- Main Content -->
    <main class="container mx-auto px-4 py-8 max-w-4xl text-center">
      <h1 class="text-2xl font-bold text-gray-800 mb-4">Tải lên ảnh của bạn</h1>
      
      <div class="mb-6">
        <h2 class="text-base font-medium text-gray-600 mb-1">Tệp phải là hình ảnh hợp lệ</h2>
        <span class="bg-blue-50 text-blue-500 text-sm px-3 py-1 rounded">JPEG, JPG, PNG</span>
      </div>
      
      <!-- Mode Toggle Button -->
      <div class="flex justify-center mb-6">
        <button 
          @click="toggleContributionMode"
          class="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
        >
          {{ isContributing ? "Chuyển sang Chế độ Mô tả AI" : "Chuyển sang Chế độ Đóng góp" }}
        </button>
      </div>
      
      <!-- Image Drop Area -->
      <div
        class="border-2 border-dashed rounded-lg p-5 text-center cursor-pointer mb-6 transition-colors max-w-full mx-auto flex items-center justify-center"
        style="min-height: 200px; width: 100%;"
        :class="{ 'border-blue-500 bg-blue-50': dragging, 'border-gray-300 hover:border-blue-300': !dragging }"
        @click="clickFileInput"
        ref="dropzone"
        @dragover="handleDragOver"
        @drop="handleDrop"
        @dragenter="handleDragEnter"
        @dragleave="handleDragLeave"
      >
        <template v-if="previewImage">
          <img
            :src="previewImage"
            alt="Xem trước hình ảnh"
            class="max-w-full mx-auto object-contain"
            style="max-height: 60vh;"
          />
        </template>
        <template v-else>
          <div class="w-full flex flex-col items-center justify-center">
          <img
            :src="mainImage"
            alt="Chọn hình ảnh hoặc kéo-thả vào đây để tải lên"
              class="max-w-full max-h-36 mx-auto"
            ref="zoneImage"
          />
          <p class="mt-4 text-gray-600" ref="zoneText">
            {{ dragging ? "Thả để tải lên hình ảnh của bạn" : "Chọn hình ảnh hoặc kéo-thả vào đây để tải lên" }}
          </p>
          </div>
        </template>
      </div>
      
      <!-- Camera Button -->
      <div v-if="isCameraSupported" class="flex justify-center mb-6">
        <button 
          @click="openCamera"
          class="flex items-center px-6 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
        >
          <span class="mr-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M4 5a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V7a2 2 0 00-2-2h-1.586a1 1 0 01-.707-.293l-1.121-1.121A2 2 0 0011.172 3H8.828a2 2 0 00-1.414.586L6.293 4.707A1 1 0 015.586 5H4zm6 9a3 3 0 100-6 3 3 0 000 6z" clip-rule="evenodd" />
            </svg>
          </span>
          Sử dụng Camera
        </button>
      </div>
      
      <!-- File Inputs (Hidden) -->
      <input
        type="file"
        id="chooseFile"
        class="hidden"
        accept="image/*"
        ref="fileInputRef"
        @change="(e) => handleAddFile(e.target.files)"
      />
      
      <input
        type="file"
        id="cameraCapture"
        class="hidden"
        accept="image/*"
        capture="environment"
        ref="cameraInputRef"
        @change="(e) => handleAddFile(e.target.files)"
      />
      
      <!-- Error Message -->
      <p v-if="clientError && !isContributing" class="text-red-500 text-center mb-4">
        {{ clientError }}
      </p>
      
      <!-- Loading Message -->
      <div v-if="isLoading && !isContributing" class="text-center text-lg font-medium text-blue-600 mb-4">
        Đang tạo mô tả...
      </div>
      
      <!-- Caption Display (AI Mode) -->
      <div v-if="imageCaption && !isContributing" class="bg-white p-6 rounded-lg shadow-md mb-6 text-center max-w-2xl mx-auto">
        <h3 class="text-xl font-medium text-blue-600 mb-5 text-center">Mô tả hình ảnh:</h3>
        
        <!-- Caption paragraph with improved styling -->
        <div class="mb-6 bg-blue-50 rounded-lg p-5 shadow-inner">
          <p class="text-gray-800 text-center text-lg leading-relaxed">{{ imageCaption }}</p>
        </div>
        
        <!-- Play button - centered with improved styling -->
        <div class="flex justify-center mb-5">
        <button 
          @click="playCaption" 
          :disabled="isLoading"
            class="flex items-center px-6 py-3 rounded-lg transition-colors whitespace-nowrap shadow-md hover:shadow-lg"
          :class="isPlaying ? 'bg-red-500 hover:bg-red-600 text-white' : 'bg-blue-500 hover:bg-blue-600 text-white'"
        >
          <template v-if="isPlaying">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 00-1 1v4a1 1 0 001 1h4a1 1 0 001-1V8a1 1 0 00-1-1H8z" clip-rule="evenodd" />
            </svg>
            Dừng
          </template>
          <template v-else>
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd" />
            </svg>
            {{ autoPlayError ? 'Phát' : 'Nghe lại' }}
          </template>
        </button>
        </div>
        
        <p v-if="autoPlayError" class="text-sm text-gray-500 mt-2 italic">
          Lưu ý: Trình duyệt có thể đã chặn tự động phát. Bạn có thể nhấn nút phía trên để nghe.
        </p>
        
        <!-- Rating Component -->
        <div class="mt-6 border-t border-gray-100 pt-5">
          <RatingStars 
            v-if="currentImageId" 
            :imageId="currentImageId" 
            :onRatingSubmitted="handleRatingSubmitted" 
          />
        </div>
      </div>
      
      <!-- Contribution Mode -->
      <div v-if="isContributing && previewImage" class="bg-gray-50 p-6 rounded-lg shadow-sm mb-6 text-left">
        <h3 class="text-base font-medium text-gray-700 mb-2">Nhập mô tả của bạn:</h3>
        <textarea 
          v-model="userCaption"
          class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 mb-4"
          placeholder="Nhập mô tả chi tiết cho hình ảnh này..."
          rows="4"
        ></textarea>
        
        <div class="flex justify-center w-full">
          <button 
            @click="handleSaveContribution"
            :disabled="isSaving"
            class="px-6 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
            :class="{ 'opacity-70 cursor-not-allowed': isSaving }"
          >
            {{ isSaving ? "Đang lưu..." : "Lưu đóng góp" }}
          </button>
        </div>
        
        <div v-if="contributionSuccess" class="mt-4 text-green-600 font-medium">
          Cảm ơn bạn đã đóng góp!
        </div>
      </div>
  
      <!-- Auth Modal -->
      <AuthModal 
        v-if="showAuthModal" 
        @close="showAuthModal = false" 
      />
  </main>
  </div>
</template>
