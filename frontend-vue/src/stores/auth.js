import { defineStore } from 'pinia';
import axios from 'axios';
import { API_URL } from '../constants';

// API base URL từ constants.js
// const API_URL = 'http://localhost:5000';

export const useAuthStore = defineStore('auth', {
  state: () => {
    // Xử lý an toàn khi parse localStorage
    let user = null;
    try {
      const userString = localStorage.getItem('user');
      if (userString) {
        user = JSON.parse(userString);
      }
    } catch (error) {
      console.error('Error parsing user from localStorage:', error);
      // Nếu có lỗi, xóa dữ liệu không hợp lệ
      localStorage.removeItem('user');
    }
    
    return {
      token: localStorage.getItem('token') || null,
      user: user,
      isLoading: false,
      error: null,
      isUpdating: false
    };
  },
  
  getters: {
    isAuthenticated: (state) => !!state.token,
    currentUser: (state) => state.user,
    isAdmin: (state) => state.user?.isAdmin === true || state.user?.is_admin === true,
  },
  
  actions: {
    async login(username, password) {
      this.isLoading = true;
      this.error = null;
      
      try {
        const response = await axios.post(`${API_URL}/api/auth/login`, {
          username,
          password
        });
        
        const { token, user } = response.data;
        
        this.token = token;
        this.user = user;
        
        localStorage.setItem('token', token);
        localStorage.setItem('user', JSON.stringify(user));
        
        return user;
      } catch (error) {
        this.error = error.response?.data?.message || 'Đăng nhập thất bại';
        throw error;
      } finally {
        this.isLoading = false;
      }
    },
    
    async register(name, username, email, password) {
      this.isLoading = true;
      this.error = null;
      
      try {
        const response = await axios.post(`${API_URL}/api/auth/register`, {
          username,
          password,
          email,
          full_name: name
        });
        
        const { token, user } = response.data;
        
        this.token = token;
        this.user = user;
        
        localStorage.setItem('token', token);
        localStorage.setItem('user', JSON.stringify(user));
        
        return user;
      } catch (error) {
        this.error = error.response?.data?.message || 'Đăng ký thất bại';
        throw error;
      } finally {
        this.isLoading = false;
      }
    },
    
    logout() {
      this.token = null;
      this.user = null;
      
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    },
    
    updateUserProfile(userData) {
      console.log('Auth store: updating user profile with:', userData);
      console.log('Auth store: current user before update:', this.user);
      
      // Make sure we're updating with the correct property names
      // Backend might use full_name while frontend uses fullName
      const normalizedData = { ...userData };
      
      // Create a new user object with the updated data
      this.user = { ...this.user, ...normalizedData };
      
      console.log('Auth store: updated user:', this.user);
      
      // Update localStorage to ensure persistence between page refreshes
      try {
        localStorage.setItem('user', JSON.stringify(this.user));
      } catch (error) {
        console.error('Error storing user in localStorage:', error);
      }
      
      // Force a reactivity trigger by creating a completely new object
      try {
        this.user = JSON.parse(JSON.stringify(this.user));
      } catch (error) {
        console.error('Error cloning user object:', error);
      }
      
      // Trigger a custom event that components can listen for
      window.dispatchEvent(new CustomEvent('user-profile-updated', { 
        detail: this.user 
      }));
    },
    
    async refreshUserProfile() {
      if (!this.token) return null;
      
      try {
        console.log('Refreshing user profile from API');
        
        // Get the full profile data
        const response = await axios.get(`${API_URL}/api/profile`, {
          headers: {
            'Authorization': `Bearer ${this.token}`
          }
        });
        
        if (response.data.success && response.data.user) {
          console.log('Got fresh profile data:', response.data.user);
          this.updateUserProfile(response.data.user);
          return response.data.user;
        }
        
        return null;
      } catch (error) {
        console.error('Error refreshing user profile:', error);
        return null;
      }
    },
    
    updateToken(newToken) {
      if (newToken) {
        this.token = newToken;
        localStorage.setItem('token', newToken);
      }
    }
  }
}); 