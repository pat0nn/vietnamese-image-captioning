import { useState } from 'react';
import styles from '../../styles/auth.module.css';
import { useAuth } from './AuthContext';

const AuthModal = ({ onClose }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const { login, register, error } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    try {
      if (isLogin) {
        const success = await login(username, password);
        if (success) {
          onClose();
        }
      } else {
        const success = await register(username, password);
        if (success) {
          onClose();
        }
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className={styles.authModalOverlay}>
      <div className={styles.authModal}>
        <div className={styles.authHeader}>
          <h2>{isLogin ? 'Đăng nhập' : 'Đăng ký tài khoản'}</h2>
          <button 
            className={styles.closeButton} 
            onClick={onClose}
            aria-label="Đóng"
          >
            &times;
          </button>
        </div>

        <form onSubmit={handleSubmit} className={styles.authForm}>
          <div className={styles.formGroup}>
            <label htmlFor="username">Tên đăng nhập</label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Nhập tên đăng nhập"
              required
            />
          </div>
          
          <div className={styles.formGroup}>
            <label htmlFor="password">Mật khẩu</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Nhập mật khẩu"
              required
            />
          </div>

          {error && <div className={styles.error}>{error}</div>}

          <button 
            type="submit" 
            className={styles.authButton}
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Đang xử lý...' : isLogin ? 'Đăng nhập' : 'Đăng ký'}
          </button>
        </form>

        <div className={styles.switchMode}>
          {isLogin ? (
            <p>Chưa có tài khoản? <button onClick={() => setIsLogin(false)}>Đăng ký ngay</button></p>
          ) : (
            <p>Đã có tài khoản? <button onClick={() => setIsLogin(true)}>Đăng nhập</button></p>
          )}
        </div>
      </div>
    </div>
  );
};

export default AuthModal; 