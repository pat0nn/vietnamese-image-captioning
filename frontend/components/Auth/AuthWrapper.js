import { useEffect, useState } from 'react';
import { useAuth } from './AuthContext';
import { toast } from 'react-toastify';

// Component to handle auth state and errors
const AuthWrapper = ({ children }) => {
  const { loading, error, user } = useAuth();
  const [hasShownWelcome, setHasShownWelcome] = useState(false);

  // Xử lý lỗi xác thực
  useEffect(() => {
    // Show toast if auth error
    if (error) {
      toast.error(error);
    }
  }, [error]);

  // Xử lý thông báo chào mừng khi đăng nhập thành công
  useEffect(() => {
    // Show welcome message on successful login
    if (user && !hasShownWelcome) {
      toast.success(`Xin chào, ${user.username}!`, { 
        toastId: 'welcome-toast', // Prevent duplicate toasts
        autoClose: 3000
      });
      setHasShownWelcome(true);
    }
  }, [user, hasShownWelcome]);

  // Đặt lại trạng thái khi đăng xuất
  useEffect(() => {
    if (!user) {
      setHasShownWelcome(false);
    }
  }, [user]);

  // Hiển thị loader khi đang kiểm tra trạng thái đăng nhập
  if (loading) {
    return <div className="auth-loading">Đang tải...</div>;
  }

  return children;
};

export default AuthWrapper; 