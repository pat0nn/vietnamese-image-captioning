import { useState } from 'react';
import Link from 'next/link';
import { useAuth } from './AuthContext';
import AuthModal from './AuthModal';
import styles from '../../styles/auth.module.css';

const AuthNav = () => {
  const { user, loading, logout, isAuthenticated } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);

  const handleLogout = async () => {
    await logout();
    setShowDropdown(false);
  };

  const toggleDropdown = () => {
    setShowDropdown(!showDropdown);
  };

  if (loading) {
    return <div>Đang tải...</div>;
  }

  return (
    <div className={styles.authStatus}>
      {isAuthenticated ? (
        <div className={styles.userDropdown}>
          <button onClick={toggleDropdown} className={styles.username}>
            {user.username} ▼
          </button>
          
          {showDropdown && (
            <div className={styles.dropdownMenu}>
              <Link href="/profile">
                <div className={styles.dropdownItem}>Hồ sơ của tôi</div>
              </Link>
              <div 
                className={styles.dropdownItem}
                onClick={handleLogout}
              >
                Đăng xuất
              </div>
            </div>
          )}
        </div>
      ) : (
        <>
          <button 
            onClick={() => setShowAuthModal(true)}
            className={styles.loginButton}
          >
            Đăng nhập
          </button>
        </>
      )}

      {showAuthModal && (
        <AuthModal onClose={() => setShowAuthModal(false)} />
      )}
    </div>
  );
};

export default AuthNav; 