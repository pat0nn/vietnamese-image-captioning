import axios from "axios";
import { useState } from "react";
import Cookies from 'js-cookie';
import apiConfig from './apiConfig';

const TOKEN_KEY = 'auth_token';
const API_URL = apiConfig.baseURL;
const IMAGE_URL = apiConfig.imageBaseURL;

// Save token to localStorage and Cookies for redundancy
export const saveToken = (token) => {
  console.log(`Saving token: ${token ? token.substring(0, 15) + '...' : 'null or undefined'}`);
  
  if (!token) {
    console.warn('Attempt to save empty token');
    return;
  }
  
  try {
    console.log('Saving token to storage...');
    
    // Primary storage: localStorage
    localStorage.setItem(TOKEN_KEY, token);
    console.log('Token saved to localStorage');
    
    // Secondary storage: Cookies
    Cookies.set('token', token, { 
      expires: 30,
      path: '/',
      sameSite: 'none',
      secure: true
    });
    console.log('Token saved to cookie');
    
    // Verify saved token
    const savedToken = getToken();
    console.log(`Token verification - Retrieved: ${savedToken ? savedToken.substring(0, 15) + '...' : 'null'}`);
  } catch (error) {
    console.error('Error saving token:', error);
  }
};

// Get token from localStorage or Cookies
export const getToken = () => {
  let token = null;
  
  // Try localStorage first
  try {
    token = localStorage.getItem(TOKEN_KEY);
    if (token) {
      console.log(`Token found in localStorage: ${token.substring(0, 15)}...`);
      return token;
    }
  } catch (e) {
    console.warn('Error reading from localStorage:', e);
  }
  
  // If not found in localStorage, try cookies
  try {
    token = Cookies.get('token');
    if (token) {
      console.log(`Token found in cookies: ${token.substring(0, 15)}...`);
      // Sync to localStorage if only found in cookies
      try {
        localStorage.setItem(TOKEN_KEY, token);
        console.log('Token from cookies synced to localStorage');
      } catch (e) {
        console.warn('Error syncing token to localStorage:', e);
      }
      return token;
    }
  } catch (e) {
    console.warn('Error reading from cookies:', e);
  }
  
  console.log('No token found in storage');
  return null;
};

// Clear token from both storage methods
export const clearToken = () => {
  console.log('Clearing token from storage');
  try {
    localStorage.removeItem(TOKEN_KEY);
    console.log('Token removed from localStorage');
  } catch (e) {
    console.warn('Error removing from localStorage:', e);
  }
  
  try {
    Cookies.remove('token', { path: '/' });
    console.log('Token removed from cookies');
  } catch (e) {
    console.warn('Error removing from cookies:', e);
  }
  
  // Verify token is cleared
  const remainingToken = getToken();
  if (remainingToken) {
    console.warn(`WARNING: Token still exists after clearing: ${remainingToken.substring(0, 15)}...`);
  } else {
    console.log('Token successfully cleared from all storage');
  }
};

// Tạo mới một instance của axios cho API calls
const api = axios.create({
  baseURL: API_URL,
  // withCredentials: false khi sử dụng proxy trên cùng domain 
  // tránh lỗi CORS
  withCredentials: false,
  headers: {
    'Content-Type': 'application/json',
    ...apiConfig.headers
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
    return config;
  },
  (error) => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Xử lý các lỗi từ phía server
api.interceptors.response.use(
  (response) => {
    // Nếu response chứa token mới, lưu token
    if (response.data && response.data.token) {
      console.log('New token received in response, updating');
      saveToken(response.data.token);
    }
    return response;
  },
  (error) => {
    console.error('API error:', error);
    
    // Kiểm tra lỗi mạng
    if (!error.response) {
      console.error('Network error - no response from server');
      return Promise.reject({
        message: 'Không thể kết nối đến máy chủ. Vui lòng kiểm tra kết nối mạng.',
        originalError: error
      });
    }
    
    // Xử lý lỗi xác thực
    if (error.response && error.response.status === 401) {
      console.warn('401 Unauthorized error - clearing token');
      clearToken();
      
      // Dispatch event để thông báo cho người dùng
      window.dispatchEvent(new CustomEvent('auth-error', { 
        detail: { message: 'Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.' } 
      }));
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
  try {
    console.log(`Đang đăng nhập với tài khoản: ${username}`);
    const response = await api.post('/login', { username, password });
    console.log('Đăng nhập thành công');
    return response.data;
  } catch (error) {
    console.error('Lỗi đăng nhập:', error);
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
  try {
    // Sử dụng API instance thay vì axios.post
    const response = await api.post('/caption', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      }
    });
    console.log('Caption API response:', response.status);
    return response.data;
  } catch (error) {
    console.error('Get caption error:', error);
    throw error;
  }
};

export const contributeImage = async (formData) => {
  console.log('Contributing image');
  try {
    // Sử dụng API instance thay vì axios.post
    const response = await api.post('/contribute', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      }
    });
    console.log('Contribute API response:', response.status);
    return response.data;
  } catch (error) {
    console.error('Contribute error:', error);
    
    if (error.response && error.response.status === 401) {
      console.log('Unauthorized contribution attempt, clearing token');
      clearToken();
    }
    
    throw error;
  }
};

export const getUserContributions = async () => {
  try {
    console.log('Getting user contributions');
    const response = await api.get('/user/contributions');
    console.log('Get user contributions response status:', response.status);
    
    // Kiểm tra response có phải JSON hay không
    if (response.data && response.data.contributions) {
      // Cập nhật đường dẫn ảnh để sử dụng proxy
      if (response.data.contributions.length > 0) {
        console.log(`Found ${response.data.contributions.length} contributions`);
      } else {
        console.log('No contributions found');
      }
      return response.data;
    } else {
      console.warn('Invalid response format', response);
      return { contributions: [] };
    }
  } catch (error) {
    console.error('Get contributions error:', error);
    return { contributions: [] }; // Trả về mảng rỗng để tránh lỗi UI
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