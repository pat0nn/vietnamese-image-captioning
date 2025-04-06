import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import styles from '../styles/admin.module.css';

export default function Admin() {
  const [contributions, setContributions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // API base URL from environment variable or default
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL?.replace('/api', '') || 'http://localhost:5000';

  useEffect(() => {
    fetchContributions();
  }, []);

  const fetchContributions = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/contributions`);
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Không thể lấy danh sách đóng góp');
      }
      
      setContributions(data.contributions || []);
    } catch (error) {
      console.error('Error fetching contributions:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Head>
        <title>Quản lý Đóng góp - Mô tả Hình ảnh</title>
      </Head>
      <div className={styles.container}>
        <h1 className={styles.title}>Quản lý Đóng góp</h1>
        <p className={styles.subtitle}>Xem tất cả hình ảnh và mô tả do người dùng đóng góp</p>
        
        {error && <div className={styles.error}>{error}</div>}
        
        {loading ? (
          <div className={styles.loading}>Đang tải đóng góp...</div>
        ) : contributions.length === 0 ? (
          <div className={styles.empty}>Không tìm thấy đóng góp nào</div>
        ) : (
          <div className={styles.grid}>
            {contributions.map((item) => (
              <div key={item.id} className={styles.card}>
                <img 
                  src={`${API_BASE_URL}/${item.image_path}`} 
                  alt={`Đóng góp ${item.id}`}
                  className={styles.image}
                />
                <div className={styles.cardContent}>
                  <div className={styles.captionBox}>
                    <h3>Mô tả của người dùng:</h3>
                    <p>{item.user_caption || "Không có mô tả người dùng"}</p>
                  </div>
                  <div className={styles.captionBox}>
                    <h3>Mô tả AI:</h3>
                    <p>{item.ai_caption || "Không có mô tả AI"}</p>
                  </div>
                  <div className={styles.metadata}>
                    <p>ID: {item.image_id}</p>
                    <p>Thêm: {new Date(item.created_at).toLocaleString()}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
        
        <button 
          className={styles.backButton}
          onClick={() => window.location.href = '/'}
        >
          Quay lại Trang Tải lên
        </button>
      </div>
    </>
  );
} 