<script setup>
import Footer from '../components/Footer.vue';
</script>

<template>
  <div class="page-container">
    <div class="about flex-grow">
    <h1>Giới thiệu về dự án</h1>
    </div>
    
    <!-- Footer -->
    <Footer />
  </div>
</template>

<style>
.page-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.flex-grow {
  flex: 1;
}

@media (min-width: 1024px) {
  .about {
    min-height: 70vh;
    display: flex;
    align-items: center;
  }
}

/* Mobile-specific styles to push footer down */
@media (max-width: 768px) {
  .page-container {
    min-height: 120vh;
  }
  
  .flex-grow {
    min-height: 100vh;
    padding-bottom: 2rem;
  }
}

@media (max-width: 480px) {
  .page-container {
    min-height: 130vh;
  }
  
  .flex-grow {
    min-height: 110vh;
    padding-bottom: 3rem;
  }
}
</style>
