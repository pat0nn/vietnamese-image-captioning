/**
 * Cấu hình API cho kết nối backend
 * 
 * Khi deploy frontend lên Azure Static Web Apps và backend sử dụng ngrok,
 * bạn cần cập nhật BACKEND_URL mỗi khi ngrok URL thay đổi.
 * 
 * Để cập nhật: Chỉ cần thay đổi giá trị NGROK_URL và lưu file này.
 */

// URL ngrok hiện tại (thay đổi khi tunnel mới được tạo)
const NGROK_URL = 'https://3a9d-116-96-47-45.ngrok-free.app';

// URL API cho môi trường phát triển
const DEV_API_URL = 'http://localhost:5000/api';

// URL API cho production (sử dụng ngrok) 
const PROD_API_URL = `${NGROK_URL}/api`;

// Chọn URL dựa trên môi trường
const API_URL = process.env.NODE_ENV === 'production' 
  ? PROD_API_URL 
  : process.env.NEXT_PUBLIC_API_URL || DEV_API_URL;

// Export cấu hình để sử dụng trong ứng dụng
export const apiConfig = {
  baseURL: API_URL,
  imageBaseURL: NGROK_URL,
  isDevelopment: process.env.NODE_ENV !== 'production'
};

export default apiConfig; 