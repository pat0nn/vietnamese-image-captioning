<script setup>
// Footer component for Vietnamese Image Captioning project
</script>

<template>
  <footer class="footer">
    <div class="footer-container">
      <div class="footer-logo">
        <img src="/logo-dark.svg" alt="Logo" class="logo-image" />
      </div>
      
      <div class="footer-content">
        <div class="footer-section">
          <h3>Thông tin liên hệ</h3>
          <p><strong>Họ tên:</strong> Phạm Bá Trọng</p>
          <p><strong>Số điện thoại:</strong> 0355917173</p>
          <p><strong>Email:</strong> <a href="mailto:phambatrong.dev@gmail.com">phambatrong.dev@gmail.com</a></p>
        </div>
        
        <div class="footer-section">
          <h3>Thông tin đồ án</h3>
          <p>Sản phẩm nằm trong ĐATN 2025 của Sinh viên Phạm Bá Trọng</p>
          <p><strong>Người hướng dẫn:</strong> Ths. Phạm Việt Anh</p>
          <p><strong>Trường:</strong> Đại học Công nghiệp Hà Nội</p>
        </div>
      </div>
    </div>
  </footer>
  

</template>

<style scoped>
.footer {
    padding:
30px 0 0;
  background:
url(https://www.haui.edu.vn/dnn/web/haui/assets/images/footer.png) #0d4e96 no-repeat center;
  position: relative;
}



.footer-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  z-index: 1;
}

.footer-logo {
  margin-bottom: 1.5rem;
  padding: 10px;
  border-radius: 5px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.logo-image {
  height: 60px;
}

.footer-content {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 2rem;
  width: 100%;
}

.footer-section {
  flex: 1;
  min-width: 250px;
}

.footer-section h3 {
  color: #ffffff;
  margin-bottom: 1rem;
  font-size: 1.2rem;
  font-weight: bold;
  position: relative;
  padding-bottom: 0.5rem;
}

.footer-section h3:after {
  content: '';
  position: absolute;
  left: 0;
  bottom: 0;
  width: 50px;
  height: 2px;
  background-color: #ffffff;
}

.footer-section p {
  margin: 0.5rem 0;
  color: #e5e7eb;
}

.footer-section a {
  color: #ffffff;
  text-decoration: none;
}

.footer-section a:hover {
  text-decoration: underline;
  color: #f0f0f0;
}

.copyright-section {
  background-color: #083970;
  padding: 1rem 0;
  color: #ffffff;
  width: 100%;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.copyright {
  text-align: center;
}

.copyright p {
  margin: 0;
  font-size: 0.9rem;
}

.copyright a {
  color: #ffffff;
  text-decoration: none;
}

.copyright a:hover {
  text-decoration: underline;
}

@media (min-width: 768px) {
  .footer-container {
    flex-direction: row;
    align-items: flex-start;
  }
  
  .footer-logo {
    margin-right: 2rem;
    margin-bottom: 0;
  }
  
  .footer-content {
    justify-content: flex-start;
  }
}
</style> 