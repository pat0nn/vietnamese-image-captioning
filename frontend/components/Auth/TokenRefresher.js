import { useEffect, useRef } from 'react';
import { useAuth } from './AuthContext';
import { getCurrentUser, getToken } from '../../utils/api';

const TokenRefresher = () => {
  const { isAuthenticated, user } = useAuth();
  const timerRef = useRef(null);
  const REFRESH_INTERVAL = 5 * 60 * 1000; // 5 minutes

  // Refresh token periodically if user is authenticated
  useEffect(() => {
    const refreshToken = async () => {
      if (isAuthenticated) {
        const token = getToken();
        if (!token) {
          console.warn('TokenRefresher: No token found for refresh');
          return;
        }
        
        console.log('TokenRefresher: Refreshing token...');
        try {
          const response = await getCurrentUser(); // Validates token with server
          if (response && response.authenticated) {
            console.log('TokenRefresher: Token refresh successful');
          } else {
            console.warn('TokenRefresher: Token validation returned unexpected data');
          }
        } catch (error) {
          console.error('TokenRefresher: Token refresh failed', error);
          // Không xóa token ở đây, để AuthContext xử lý qua interceptor
        }
      }
    };

    const setupRefreshTimer = () => {
      if (isAuthenticated) {
        console.log(`TokenRefresher: Setting up refresh timer (${REFRESH_INTERVAL / 1000}s)`);
        
        // Clear any existing timer
        if (timerRef.current) {
          clearInterval(timerRef.current);
        }
        
        // Set up new timer
        timerRef.current = setInterval(refreshToken, REFRESH_INTERVAL);
        
        // Also refresh immediately
        refreshToken();
      }
    };

    setupRefreshTimer();

    // Setup event listeners for window focus/blur
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible' && isAuthenticated) {
        console.log('TokenRefresher: Page became visible, refreshing token');
        refreshToken();
      }
    };

    const handleOnline = () => {
      if (isAuthenticated) {
        console.log('TokenRefresher: Network reconnected, refreshing token');
        refreshToken();
      }
    };

    // Initialize with any stored token
    if (isAuthenticated) {
      console.log('TokenRefresher: Initializing with stored token');
      refreshToken();
    }

    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('online', handleOnline);

    return () => {
      // Clean up
      console.log('TokenRefresher: Cleaning up timers and event listeners');
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('online', handleOnline);
    };
  }, [isAuthenticated, user]);

  // This component doesn't render anything
  return null;
};

export default TokenRefresher; 