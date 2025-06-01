// Các class name cho theme
export const DARK_CLASS_NAME = 'dark';
export const DARK_COLOR_THEME = 'dark';
export const LIGHT_CLASS_NAME = 'light';
export const LIGHT_COLOR_THEME = 'light';
export const HIDDEN_CLASS_NAME = 'hidden';

// Cấu hình API
export const API_URL = (function() {
  // Nếu đang ở development environment (localhost)
  if (typeof window !== 'undefined' && window.location.hostname === 'localhost') {
    return 'http://localhost:5000'; // Local development API
  }
  
  // Khi deploy lên Firebase hoặc các hosting khác, luôn trỏ đến Cloud Run backend
  return 'https://flask-backend-668247880976.asia-east1.run.app';
})();

// Base URL for the frontend application
export const BASE_URL = (function() {
  // If running on localhost
  if (typeof window !== 'undefined' && window.location.hostname === 'localhost') {
    return 'http://localhost:5173';
  }
  // If using the production domain
  return window.location.origin;
})();

// Các màu chính cho biểu đồ
export const CHART_COLORS = {
    BLUE: '#1A56DB',     // Màu xanh lam cho đóng góp ảnh
    ORANGE: '#FDBA8C',   // Màu cam cho tạo caption
    GREEN: '#31C48D',    // Màu xanh lá cho các số liệu tích cực
    RED: '#F05252',      // Màu đỏ cho các số liệu tiêu cực
    GRAY: '#9CA3AF',     // Màu xám cho các thành phần trung tính
};

// Các khoảng thời gian cho biểu đồ
export const TIME_PERIODS = {
    TODAY: 1,
    WEEK: 7,
    MONTH: 30,
    QUARTER: 90,
};

// Cấu hình chung
export const CONFIG = {
    DASHBOARD_REFRESH_INTERVAL: 5 * 60 * 1000, // 5 phút
    TOKEN_KEY: 'auth_token',
    DEFAULT_DAYS: 7,
    // Đã sửa cấu hình để luôn sử dụng API tuyệt đối
    USE_RELATIVE_API: false,
};