import { useEffect } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import UserContributions from '../components/UserProfile/UserContributions';
import { useAuth } from '../components/Auth/AuthContext';
import AuthNav from '../components/Auth/AuthNav';
import styles from '../styles/userProfile.module.css';
import indexStyles from '../styles/index.module.css';

const ProfilePage = () => {
  const { isAuthenticated, loading } = useAuth();
  const router = useRouter();
  
  // Redirect to home if not authenticated
  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push('/');
    }
  }, [isAuthenticated, loading, router]);
  
  if (loading) {
    return <div>Đang tải...</div>;
  }
  
  if (!isAuthenticated) {
    return null; // Will redirect in the useEffect
  }

  return (
    <>
      <Head>
        <title>Hồ sơ của tôi - Ứng dụng Mô tả Hình ảnh</title>
      </Head>
      
      {/* NavBar giống trang chính */}
      <div className={indexStyles.navBar}>
        <h1 className={indexStyles.logo}>Image Caption</h1>
        <AuthNav />
      </div>
      
      <main className={styles.profileContainer}>
        {/* <div className={styles.header}>
          <h1>Hồ sơ của tôi</h1>
          <button onClick={() => router.push('/')} className={styles.backButton}>
            Quay lại trang chủ
          </button>
        </div> */}
        
        <UserContributions />
      </main>
    </>
  );
};

export default ProfilePage;