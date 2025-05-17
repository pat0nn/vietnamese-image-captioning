import { defineStore } from 'pinia'
import { loginUser } from '../../utils/adminApi'
import { CONFIG } from '../../constants'
import router from '../../router'
import { BASE_URL } from '../../constants'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: null,
    loading: false,
    error: null,
    initialized: false
  }),
  
  getters: {
    isAuthenticated: (state) => !!state.token,
    isAdmin: (state) => state.user?.is_admin || false,
    currentUser: (state) => state.user
  },
  
  actions: {
    async initialize() {
      console.log('Initializing admin auth store');
      if (this.initialized) {
        console.log('Admin auth store already initialized, skipping');
        return;
      }
      
      // Check localStorage for token and user data
      // First try the admin token key, then fallback to the main site token
      const adminToken = localStorage.getItem(CONFIG.TOKEN_KEY);
      const mainToken = localStorage.getItem('token');
      const token = adminToken || mainToken;
      const userJson = localStorage.getItem('user');
      
      console.log('Admin token:', adminToken ? 'exists' : 'missing');
      console.log('Main token:', mainToken ? 'exists' : 'missing');
      console.log('User JSON:', userJson ? 'exists' : 'missing');
      
      if (token) {
        this.token = token;
        console.log('Setting token in admin auth store');
        
        // If using the main token but missing admin token, set it
        if (mainToken && !adminToken) {
          console.log('Setting main token as admin token');
          localStorage.setItem(CONFIG.TOKEN_KEY, mainToken);
        }
        
        if (userJson) {
          try {
            // Kiểm tra chắc chắn userJson không phải là undefined hoặc null
            if (!userJson) {
              throw new Error('User data is empty');
            }
            
            const user = JSON.parse(userJson);
            console.log('Parsed user data:', user);
            
            // Check if the user has admin privileges
            if (user && (user.is_admin === true || user.isAdmin === true)) {
              console.log('User has admin privileges, setting user in admin auth store');
              // Ensure the is_admin flag is set consistently
              this.user = {
                ...user,
                is_admin: true
              };
              
              console.log('Admin user set:', this.user);
              
              // Make sure we're using the right token
              if (adminToken) {
                // Validate that the token is still valid by checking its expiration
                try {
                  const tokenParts = adminToken.split('.');
                  if (tokenParts.length === 3) {
                    const payload = JSON.parse(atob(tokenParts[1]));
                    const expTime = payload.exp * 1000; // Convert to milliseconds
                    console.log('Token expiration:', new Date(expTime));
                    console.log('Current time:', new Date());
                    
                    if (Date.now() > expTime) {
                      console.warn('Admin token expired, redirecting to login');
                      this.token = null;
                      this.user = null;
                      localStorage.removeItem(CONFIG.TOKEN_KEY);
                      localStorage.removeItem('token');
                      localStorage.removeItem('user');
                      router.push('/admin/login?reason=session_expired');
                      return;
                    }
                  }
                } catch (e) {
                  console.error('Error validating token:', e);
                }
              }
            } else {
              console.warn('User is not an admin, redirecting to login');
              this.token = null;
              this.user = null;
              router.push('/admin/login');
            }
          } catch (e) {
            console.error('Error parsing user data from localStorage:', e);
            this.user = null;
            this.token = null;
            localStorage.removeItem(CONFIG.TOKEN_KEY);
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            router.push('/admin/login');
          }
        } else {
          // We have a token but no user data, redirect to login
          console.log('Token found but no user data, redirecting to login');
          this.token = null;
          localStorage.removeItem(CONFIG.TOKEN_KEY);
          localStorage.removeItem('token');
          router.push('/admin/login');
        }
      } else {
        // No token found, redirect to login
        console.log('No token found, redirecting to login');
        this.user = null;
        router.push('/admin/login');
      }
      
      this.initialized = true;
      console.log('Admin auth store initialization complete');
    },
    
    async login(username, password, remember = false) {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await loginUser(username, password);
        
        if (response && response.success) {
          // Check if the user is an admin
          if (!response.user.is_admin) {
            this.error = 'Chỉ tài khoản admin mới có quyền truy cập trang quản trị';
            // Remove any saved token since they don't have admin access
            localStorage.removeItem(CONFIG.TOKEN_KEY);
            localStorage.removeItem('token'); // Also clear main site token
            localStorage.removeItem('user');
            return false;
          }
          
          this.token = response.token;
          this.user = response.user;
          
          // Save to localStorage for admin site
          localStorage.setItem(CONFIG.TOKEN_KEY, response.token);
          // Also save to localStorage for main site for seamless integration
          localStorage.setItem('token', response.token);
          
          try {
            localStorage.setItem('user', JSON.stringify(response.user));
          } catch (e) {
            console.error('Error storing user data in localStorage:', e);
          }
          
          if (remember) {
            localStorage.setItem('remember_login', 'true');
          } else {
            localStorage.removeItem('remember_login');
          }
          
          // Get the redirect path or go to dashboard
          const redirectPath = router.currentRoute.value.query.redirect || '/';
          router.push(redirectPath);
          
          return true;
        } else {
          this.error = 'Login failed. Please check your credentials.';
          return false;
        }
      } catch (error) {
        console.error('Login error:', error);
        this.error = error.message || 'An unexpected error occurred';
        return false;
      } finally {
        this.loading = false;
      }
    },
    
    logout() {
      // Clear state
      this.token = null;
      this.user = null;
      
      // Clear localStorage - both admin and main tokens
      localStorage.removeItem(CONFIG.TOKEN_KEY);
      localStorage.removeItem('token'); // Also clear main site token
      localStorage.removeItem('user');
      
      // Redirect to main site homepage using BASE_URL
      window.location.href = BASE_URL || '/';
    },
    
    clearError() {
      this.error = null;
    }
  }
}) 