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
  let token = null;
  
  // Try localStorage
  try {
    token = localStorage.getItem(TOKEN_KEY);
    if (token) {
      console.log(`Token found in localStorage: ${token.substring(0, 15)}...`);
      return token;
    }
  } catch (e) {
    console.warn('Error reading from localStorage:', e);
  }
  
  console.log('No token found in storage');
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
    console.error('API error:', error);
    
    // If 401 Unauthorized error, clear token and notify
    if (error.response && error.response.status === 401) {
      console.warn('401 Unauthorized error - clearing authentication');
      clearToken();
      // You might dispatch an event or action to update UI
      window.dispatchEvent(new CustomEvent('auth-error', { 
        detail: { message: 'Your session has expired. Please log in again.' } 
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
    console.log(`Gửi request đến: ${API_URL}/caption`);
    const response = await axios.post(`${API_URL}/caption`, formData, {
      withCredentials: false, // Không sử dụng cookies
      headers
    });
    console.log('Caption API response:', response.status);
    return response.data;
  } catch (error) {
    console.error('Get caption error:', error.message || error);
    console.error('Error details:', error.response?.data || 'No response data');
    console.error('Error getting caption with URL:', `${API_URL}/caption`);
    throw error;
  }
};

export const contributeImage = async (formData) => {
  console.log('Contributing image');
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
    
    const response = await axios.post(`${API_URL}/contribute`, formData, {
      withCredentials: false, // Không sử dụng cookies
      headers
    });
    console.log('Contribute API response:', response.status);
    return response.data;
  } catch (error) {
    console.error('Contribute error:', error.response?.data || error.message);
    
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
  
  try {
    console.log('Sending request to get user contributions...');
    const response = await api.get('/user/contributions');
    console.log('User contributions response status:', response.status);
    console.log('User contributions data:', response.data);
    return response.data;
  } catch (error) {
    console.error('Get contributions error:', error);
    console.error('Error details:', error.response?.data || 'No response data');
    console.error('Error status:', error.response?.status);
    
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