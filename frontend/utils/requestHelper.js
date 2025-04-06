import axios from "axios";
import { useState } from "react";

const TOKEN_KEY = 'auth_token';
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api';

// Save token to localStorage
export const saveToken = (token) => {
  console.log(`Saving token: ${token ? token.substring(0, 15) + '...' : 'null or undefined'}`);
  
  if (!token) {
    console.warn('Attempt to save empty token');
    return;
  }
  
  try {
    console.log('Saving token to localStorage...');
    
    // Primary storage: localStorage
    localStorage.setItem(TOKEN_KEY, token);
    console.log('Token saved to localStorage');
    
    // Verify saved token
    const savedToken = getToken();
    console.log(`Token verification - Retrieved: ${savedToken ? savedToken.substring(0, 15) + '...' : 'null'}`);
  } catch (error) {
    console.error('Error saving token:', error);
  }
};

// Get token from localStorage
export const getToken = () => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem(TOKEN_KEY);
    console.log('Token found in localStorage:', token ? `${token.substring(0, 15)}...` : 'null');
    return token;
  }
  return null;
};

// Clear token
export const clearToken = () => {
  console.log('Clearing token from storage');
  try {
    localStorage.removeItem(TOKEN_KEY);
    console.log('Token removed from localStorage');
  } catch (e) {
    console.warn('Error removing from localStorage:', e);
  }
  
  // Verify token is cleared
  const remainingToken = getToken();
  if (remainingToken) {
    console.warn(`WARNING: Token still exists after clearing: ${remainingToken.substring(0, 15)}...`);
  } else {
    console.log('Token successfully cleared from storage');
  }
};

// Track ngrok URL confirmation
export const isNgrokConfirmed = (url) => {
  if (typeof window !== 'undefined') {
    const confirmedUrls = localStorage.getItem('confirmed_ngrok_urls');
    if (confirmedUrls) {
      try {
        const urlsArray = JSON.parse(confirmedUrls);
        return urlsArray.includes(url);
      } catch (e) {
        return false;
      }
    }
  }
  return false;
};

export const markNgrokAsConfirmed = (url) => {
  if (typeof window !== 'undefined') {
    let confirmedUrls = [];
    const existingUrls = localStorage.getItem('confirmed_ngrok_urls');
    
    if (existingUrls) {
      try {
        confirmedUrls = JSON.parse(existingUrls);
      } catch (e) {
        confirmedUrls = [];
      }
    }
    
    if (!confirmedUrls.includes(url)) {
      confirmedUrls.push(url);
      localStorage.setItem('confirmed_ngrok_urls', JSON.stringify(confirmedUrls));
    }
  }
};

// Function to verify and confirm ngrok URL
export const verifyNgrokUrl = async () => {
  if (!API_URL.includes('ngrok')) {
    return true; // Không phải ngrok URL, không cần xác nhận
  }
  
  if (isNgrokConfirmed(API_URL)) {
    console.log('Ngrok URL đã được xác nhận trước đó:', API_URL);
    return true;
  }
  
  try {
    console.log('Đang xác nhận Ngrok URL:', API_URL);
    // Tạo một tab mới để xác nhận URL
    if (typeof window !== 'undefined') {
      const testUrl = `${API_URL}/ngrok-ready?_ngrok_skip_browser_warning=true`;
      const newWindow = window.open(testUrl, '_blank');
      
      // Đánh dấu URL đã được mở để xác nhận
      console.log('Đã mở tab mới để xác nhận URL');
      
      // Thông báo cho người dùng
      alert('Vui lòng xác nhận URL ngrok trong tab mới vừa mở.\nNhấn "Visit Site" trên trang ngrok.');
      
      return false;
    }
  } catch (e) {
    console.error('Lỗi khi xác nhận ngrok URL:', e);
    return false;
  }
};

const api = axios.create({
  baseURL: API_URL,
  withCredentials: false, // Không sử dụng cookies
  headers: {
    'Content-Type': 'application/json',
  }
});

// Add token to requests if available
api.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token) {
      console.log(`Adding token to request: ${token.substring(0, 15)}...`);
      config.headers['Authorization'] = `Bearer ${token}`;
    } else {
      console.log('No token available for request');
    }
    
    // Thêm param ngrok skip browser warning cho tất cả request
    // Kiểm tra xem URL hiện tại có chứa ngrok không
    if (API_URL.includes('ngrok')) {
      // Chỉ thêm tham số nếu chưa tồn tại trong URL
      if (!config.url.includes('_ngrok_skip_browser_warning=true')) {
        const separator = config.url.includes('?') ? '&' : '?';
        config.url = `${config.url}${separator}_ngrok_skip_browser_warning=true`;
        console.log(`Modified URL with ngrok param: ${config.url}`);
      }
    }
    
    return config;
  },
  (error) => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Handle response and detect auth errors
api.interceptors.response.use(
  (response) => {
    // If response contains new token, update
    if (response.data && response.data.token) {
      console.log('New token received in response, updating');
      saveToken(response.data.token);
    }
    
    return response;
  },
  (error) => {
    console.error('API error:', error.message);
    if (error.response) {
      console.error('Error status:', error.response.status);
      console.error('Error data:', error.response.data);
      
      // Check if we received an HTML response (likely ngrok warning)
      const contentType = error.response.headers['content-type'] || '';
      if (contentType.includes('text/html') && API_URL.includes('ngrok')) {
        console.error('Received HTML instead of JSON. This may be the ngrok warning page.');
        // Try to verify the ngrok URL
        verifyNgrokUrl();
      }
      
      // Handle 401 Unauthorized
      if (error.response.status === 401) {
        console.log('Unauthorized, clearing token');
        clearToken();
      }
    }
    return Promise.reject(error);
  }
);

// Auth methods
export const register = async (username, password) => {
  console.log('Registering user:', username);
  try {
    const response = await api.post('/register', { username, password });
    console.log('Registration API response:', response.status);
    
    // Save token
    if (response.data && response.data.token) {
      console.log('Registration successful, saving token');
      saveToken(response.data.token);
    } else {
      console.error('Registration response missing token');
    }
    
    return response.data;
  } catch (error) {
    console.error('Registration failed:', error.response?.data || error.message);
    throw error;
  }
};

export const login = async (username, password) => {
  console.log('Logging in user:', username);
  try {
    const response = await api.post('/login', { username, password });
    console.log('Login API response:', response.status);
    
    // Save token
    if (response.data && response.data.token) {
      console.log('Login successful, saving token');
      saveToken(response.data.token);
    } else {
      console.error('Login response missing token');
    }
    
    return response.data;
  } catch (error) {
    console.error('Login failed:', error.response?.data || error.message);
    throw error;
  }
};

export const logout = async () => {
  console.log('Logging out user');
  try {
    // Send logout request
    const response = await api.post('/logout');
    console.log('Logout API response:', response.status);
    
    // Clear token regardless of response
    clearToken();
    
    return response.data;
  } catch (error) {
    console.error('Logout error:', error.response?.data || error.message);
    // Still clear token even if the request fails
    clearToken();
    throw error;
  }
};

export const getCurrentUser = async () => {
  console.log('Getting current user data');
  try {
    const token = getToken();
    if (!token) {
      console.log('No token available, skipping user fetch');
      return { authenticated: false };
    }
    
    const response = await api.get('/user');
    console.log('User data response:', response.status);
    return response.data;
  } catch (error) {
    console.error('Get user data error:', error.response?.status, error.response?.data || error.message);
    
    if (error.response && error.response.status === 401) {
      console.log('Unauthorized, clearing token');
      clearToken();
    }
    
    return { authenticated: false };
  }
};

// Image related methods
export const getImageCaption = async (formData) => {
  console.log('Getting image caption');
  console.log(`API URL được sử dụng: ${API_URL}`);
  
  // Kiểm tra và xác nhận ngrok URL nếu cần
  if (API_URL.includes('ngrok') && !isNgrokConfirmed(API_URL)) {
    console.log('Ngrok URL chưa được xác nhận, đang tự động xác nhận...');
    await verifyNgrokUrl();
    
    // Tạm dừng để cho người dùng thời gian xác nhận
    await new Promise(resolve => setTimeout(resolve, 2000));
  }
  
  const token = getToken();
  const headers = {
    'Content-Type': 'multipart/form-data',
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
    console.log('Adding token to caption request');
  }
  
  // Log FormData để debug
  console.log('FormData contents:');
  for (let pair of formData.entries()) {
    console.log(`${pair[0]}: ${pair[1] instanceof File ? pair[1].name : pair[1]}`);
  }
  
  try {
    // Thêm param ngrok
    let url = `${API_URL}/caption`;
    if (API_URL.includes('ngrok')) {
      url += '?_ngrok_skip_browser_warning=true';
      console.log(`Using URL with ngrok param: ${url}`);
    }
    
    console.log(`Gửi request đến: ${url}`);
    const response = await axios.post(url, formData, {
      withCredentials: false, // Không sử dụng cookies
      headers
    });
    
    // Nếu thành công, đánh dấu URL là đã xác nhận
    if (API_URL.includes('ngrok')) {
      markNgrokAsConfirmed(API_URL);
    }
    
    console.log('Caption API response:', response.status);
    return response.data;
  } catch (error) {
    console.error('Get caption error:', error.message || error);
    console.error('Error details:', error.response?.data || 'No response data');
    console.error('Error getting caption with URL:', `${API_URL}/caption`);
    
    // Kiểm tra nếu response là HTML
    if (error.response && error.response.headers) {
      const contentType = error.response.headers['content-type'] || '';
      if (contentType.includes('text/html') && API_URL.includes('ngrok')) {
        console.error('Received HTML instead of JSON from error. This may be the ngrok warning page.');
        
        // Mở tab để xác nhận URL
        if (!isNgrokConfirmed(API_URL)) {
          await verifyNgrokUrl();
        }
      }
    }
    
    throw error;
  }
};

export const contributeImage = async (formData) => {
  console.log('Contributing image');
  
  // Kiểm tra và xác nhận ngrok URL nếu cần
  if (API_URL.includes('ngrok') && !isNgrokConfirmed(API_URL)) {
    console.log('Ngrok URL chưa được xác nhận, đang tự động xác nhận...');
    await verifyNgrokUrl();
    
    // Tạm dừng để cho người dùng thời gian xác nhận
    await new Promise(resolve => setTimeout(resolve, 2000));
  }
  
  const token = getToken();
  const headers = {
    'Content-Type': 'multipart/form-data',
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
    console.log('Adding token to contribution request');
  } else {
    console.log('No token available for contribution request');
  }
  
  try {
    // Log formData để debug
    console.log('FormData contents:');
    for (let pair of formData.entries()) {
      console.log(pair[0] + ': ' + pair[1]);
    }
    
    // Thêm param ngrok
    let url = `${API_URL}/contribute`;
    if (API_URL.includes('ngrok')) {
      url += '?_ngrok_skip_browser_warning=true';
      console.log(`Using URL with ngrok param: ${url}`);
    }
    
    console.log(`Gửi request đến: ${url}`);
    const response = await axios.post(url, formData, {
      withCredentials: false, // Không sử dụng cookies
      headers
    });
    
    // Nếu thành công, đánh dấu URL là đã xác nhận
    if (API_URL.includes('ngrok')) {
      markNgrokAsConfirmed(API_URL);
    }
    
    console.log('Contribute API response:', response.status);
    return response.data;
  } catch (error) {
    console.error('Contribute error:', error.response?.data || error.message);
    
    // Kiểm tra nếu response là HTML
    if (error.response && error.response.headers) {
      const contentType = error.response.headers['content-type'] || '';
      if (contentType.includes('text/html') && API_URL.includes('ngrok')) {
        console.error('Received HTML instead of JSON from error. This may be the ngrok warning page.');
        
        // Mở tab để xác nhận URL
        if (!isNgrokConfirmed(API_URL)) {
          await verifyNgrokUrl();
        }
      }
    }
    
    if (error.response && error.response.status === 401) {
      console.log('Unauthorized contribution attempt, clearing token');
      clearToken();
    }
    
    throw error;
  }
};

export const getUserContributions = async () => {
  console.log('Getting user contributions');
  
  const token = getToken();
  if (!token) {
    console.log('No token available for getting user contributions');
    return { contributions: [] };
  }
  
  console.log(`Using token: ${token.substring(0, 15)}...`);
  console.log(`API URL: ${API_URL}`);
  
  // Kiểm tra và xác nhận ngrok URL nếu cần
  if (API_URL.includes('ngrok') && !isNgrokConfirmed(API_URL)) {
    console.log('Ngrok URL chưa được xác nhận, đang tự động xác nhận...');
    // Xác nhận URL trước
    await verifyNgrokUrl();
    
    // Tạm dừng để cho người dùng thời gian xác nhận
    await new Promise(resolve => setTimeout(resolve, 2000));
  }
  
  try {
    console.log('Sending request to get user contributions...');
    
    // Thêm tham số để ngăn ngrok hiển thị trang xác nhận
    const url = `${API_URL}/user/contributions?_ngrok_skip_browser_warning=true`;
    console.log(`Using URL with ngrok skip parameter: ${url}`);
    
    const response = await api.get(url);
    
    // Kiểm tra xem response có phải JSON hay HTML
    const contentType = response.headers['content-type'] || '';
    console.log(`Response content type: ${contentType}`);
    
    if (contentType.includes('text/html')) {
      console.error('Received HTML response instead of JSON. This might be the ngrok warning page.');
      console.log('Please visit the ngrok URL directly in your browser first to approve it.');
      
      // Mở tab để xác nhận URL nếu chưa xác nhận
      if (!isNgrokConfirmed(API_URL)) {
        await verifyNgrokUrl();
      }
      
      // Trả về mảng rỗng nếu nhận được HTML
      return { contributions: [] };
    }
    
    console.log('User contributions response status:', response.status);
    console.log('User contributions data:', response.data);
    
    // Nếu nhận được JSON hợp lệ, đánh dấu URL đã được xác nhận
    if (API_URL.includes('ngrok')) {
      markNgrokAsConfirmed(API_URL);
    }
    
    return response.data;
  } catch (error) {
    console.error('Get contributions error:', error);
    console.error('Error details:', error.response?.data || 'No response data');
    console.error('Error status:', error.response?.status);
    
    // Kiểm tra nếu response là HTML
    if (error.response && error.response.headers) {
      const contentType = error.response.headers['content-type'] || '';
      if (contentType.includes('text/html') && API_URL.includes('ngrok')) {
        console.error('Received HTML instead of JSON from error. This may be the ngrok warning page.');
        
        // Mở tab để xác nhận URL
        if (!isNgrokConfirmed(API_URL)) {
          await verifyNgrokUrl();
        }
      }
    }
    
    if (error.response && error.response.status === 401) {
      console.log('Unauthorized when getting contributions, clearing token');
      clearToken();
    }
    
    throw error;
  }
};

export const updateContribution = async (imageId, userCaption) => {
  console.log(`Updating contribution: ${imageId}`);
  try {
    const response = await api.put(`/contribution/${imageId}`, { userCaption });
    console.log('Update contribution response:', response.status);
    return response.data;
  } catch (error) {
    console.error('Update contribution error:', error.response?.data || error.message);
    throw error;
  }
};

export const deleteContribution = async (imageId) => {
  console.log(`Deleting contribution: ${imageId}`);
  try {
    const response = await api.delete(`/contribution/${imageId}`);
    console.log('Delete contribution response:', response.status);
    return response.data;
  } catch (error) {
    console.error('Delete contribution error:', error.response?.data || error.message);
    throw error;
  }
};

export default api;