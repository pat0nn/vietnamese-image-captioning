import { createContext, useState, useEffect, useContext } from 'react';
import api, { 
  getCurrentUser, 
  login as apiLogin, 
  register as apiRegister, 
  logout as apiLogout,
  getToken, 
  clearToken 
} from '../../utils/api';

// Create the auth context
const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Check if user is already logged in on mount
  useEffect(() => {
    const checkAuthStatus = async () => {
      try {
        console.log("Checking auth status...");
        
        // First check if we have a token in any storage method
        const token = getToken();
        console.log("Token from storage:", token ? "Found" : "Not found");
        
        if (!token) {
          console.log("No token found, finishing auth check");
          setLoading(false);
          return;
        }
        
        // If we have a token, validate it with the server
        console.log("Validating token with server...");
        try {
          const response = await getCurrentUser();
          console.log("Auth check response:", response);
          
          // Kiểm tra cấu trúc dữ liệu trả về từ API
          if (response && response.authenticated) {
            console.log("User authenticated:", response.username);
            
            // Tạo đối tượng user từ dữ liệu API
            const userData = {
              id: response.user_id,
              username: response.username
            };
            
            setUser(userData);
            console.log("User set from token:", userData);
          } else {
            console.log("Token valid but user data incomplete");
            clearToken();
          }
        } catch (err) {
          console.error("Token validation failed:", err);
          clearToken();
        }
      } catch (err) {
        console.error('Auth check error:', err);
        clearToken();
      } finally {
        setLoading(false);
      }
    };

    checkAuthStatus();
    
    // Listen for auth errors
    const handleAuthError = (event) => {
      console.log('Auth error event received:', event.detail);
      setUser(null);
      setError(event.detail.message);
    };
    
    window.addEventListener('auth-error', handleAuthError);
    
    return () => {
      window.removeEventListener('auth-error', handleAuthError);
    };
  }, []);

  // Login function
  const handleLogin = async (username, password) => {
    setError(null);
    try {
      console.log("Attempting login for:", username);
      const response = await apiLogin(username, password);
      console.log("Login response:", response);
      
      // Set user from response
      if (response && response.user) {
        setUser(response.user);
        console.log("User set from login:", response.user);
      } else if (response && response.message === 'Login successful') {
        // Kiểm tra trường hợp API trả về dạng cũ
        const userData = {
          id: response.user_id || response.id,
          username: response.username
        };
        setUser(userData);
        console.log("User set from login (legacy format):", userData);
      }
      
      return true;
    } catch (err) {
      console.error("Login error:", err);
      setError(err.response?.data?.error || 'Đăng nhập thất bại');
      return false;
    }
  };

  // Register function
  const handleRegister = async (username, password) => {
    setError(null);
    try {
      console.log("Attempting registration for:", username);
      const response = await apiRegister(username, password);
      console.log("Registration response:", response);
      
      // Set user from response
      if (response && response.user) {
        setUser(response.user);
        console.log("User set from registration:", response.user);
      } else if (response && response.message === 'User created successfully') {
        // Kiểm tra trường hợp API trả về dạng cũ
        const userData = {
          id: response.user_id || response.id, 
          username: response.username
        };
        setUser(userData);
        console.log("User set from registration (legacy format):", userData);
      }
      
      return true;
    } catch (err) {
      console.error("Registration error:", err);
      setError(err.response?.data?.error || 'Đăng ký thất bại');
      return false;
    }
  };

  // Logout function
  const handleLogout = async () => {
    setError(null);
    try {
      console.log("Logging out user:", user?.username);
      await apiLogout();
      setUser(null);
      
      return true;
    } catch (err) {
      console.error("Logout error:", err);
      // Even if server logout fails, clear local state
      setUser(null);
      setError(err.response?.data?.error || 'Đăng xuất thất bại');
      return false;
    }
  };

  const contextValue = {
    user,
    loading,
    error,
    login: handleLogin,
    register: handleRegister,
    logout: handleLogout,
    isAuthenticated: !!user
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use the auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext; 