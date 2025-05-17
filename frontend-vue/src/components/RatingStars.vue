<script setup>
import { ref } from 'vue';
import { submitRating } from '../utils/requestHelper';

const props = defineProps({
  imageId: {
    type: String,
    required: true
  },
  onRatingSubmitted: {
    type: Function,
    default: () => {}
  }
});

const rating = ref(0);
const hoveredRating = ref(0);
const isSubmitting = ref(false);
const hasRated = ref(false);

const handleMouseEnter = (star) => {
  if (!hasRated.value) {
    hoveredRating.value = star;
  }
};

const handleMouseLeave = () => {
  hoveredRating.value = 0;
};

const handleClick = async (star) => {
  if (hasRated.value || isSubmitting.value) return;
  
  rating.value = star;
  isSubmitting.value = true;
  
  try {
    await submitRating(props.imageId, star);
    hasRated.value = true;
    props.onRatingSubmitted(star);
  } catch (error) {
    console.error('Error submitting rating:', error);
    rating.value = 0;
  } finally {
    isSubmitting.value = false;
  }
};

const getStarClass = (star) => {
  if (hasRated.value) {
    return star <= rating.value ? 'text-yellow-400' : 'text-gray-300';
  }
  
  return (hoveredRating.value && star <= hoveredRating.value) || (!hoveredRating.value && star <= rating.value)
    ? 'text-yellow-400'
    : 'text-gray-300';
};
</script>

<template>
  <div class="rating-container mt-4">
    <div class="flex flex-col items-center">
      <h4 class="text-lg font-medium mb-2">Đánh giá mô tả này:</h4>
      <div class="flex space-x-1">
        <button
          v-for="star in 5"
          :key="star"
          @click="handleClick(star)"
          @mouseenter="handleMouseEnter(star)"
          @mouseleave="handleMouseLeave"
          :disabled="hasRated || isSubmitting"
          class="focus:outline-none text-2xl transition-colors duration-200"
          :class="getStarClass(star)"
        >
          ★
        </button>
      </div>
      <p v-if="hasRated" class="text-green-600 mt-2">
        Cảm ơn bạn đã đánh giá!
      </p>
      <p v-else-if="isSubmitting" class="text-gray-500 mt-2">
        Đang gửi đánh giá...
      </p>
    </div>
  </div>
</template> 