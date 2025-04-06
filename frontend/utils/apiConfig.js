/**
 * Cấu hình API cho kết nối backend
 * 
 * Khi deploy frontend lên Azure Static Web Apps, chúng ta sử dụng proxy built-in
 * để chuyển tiếp yêu cầu đến backend qua ngrok, tránh các vấn đề CORS.
 */

// Sử dụng proxy từ cùng domain trong môi trường production
const PROXY_URL = '/api'; // Azure Static Web Apps sẽ chuyển tiếp đến ngrok

// URL cho môi trường phát triển
const DEV_API_URL = 'http://localhost:5000/api';

// URL cho hình ảnh trong môi trường phát triển
const DEV_IMAGE_URL = 'http://localhost:5000';

// Chọn URL dựa trên môi trường
const API_URL = process.env.NODE_ENV === 'production' 
  ? PROXY_URL
  : process.env.NEXT_PUBLIC_API_URL || DEV_API_URL;

// Chọn URL cho hình ảnh dựa trên môi trường 
const IMAGE_URL = process.env.NODE_ENV === 'production'
  ? '/uploads' // Sử dụng proxy từ cùng origin
  : DEV_IMAGE_URL;

// Export cấu hình để sử dụng trong ứng dụng
export const apiConfig = {
  baseURL: API_URL,
  imageBaseURL: IMAGE_URL,
  isDevelopment: process.env.NODE_ENV !== 'production',
  // Các headers mặc định (không cần CORS headers khi sử dụng proxy)
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
};

// Hiển thị thông tin cấu hình trong console (để debug)
console.log('API Configuration:', {
  baseURL: apiConfig.baseURL,
  imageBaseURL: apiConfig.imageBaseURL,
  environment: process.env.NODE_ENV || 'development'
});

export default apiConfig; 