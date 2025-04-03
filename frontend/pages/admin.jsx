import { useState, useEffect } from 'react';
import Head from 'next/head';
import styles from '../styles/admin.module.css';

export default function Admin() {
  const [contributions, setContributions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchContributions();
  }, []);

  const fetchContributions = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:5000/api/contributions');
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to fetch contributions');
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
        <title>Contribution Admin - Image Captioning</title>
      </Head>
      <div className={styles.container}>
        <h1 className={styles.title}>Contributions Admin</h1>
        <p className={styles.subtitle}>View all user-contributed images and captions</p>
        
        {error && <div className={styles.error}>{error}</div>}
        
        {loading ? (
          <div className={styles.loading}>Loading contributions...</div>
        ) : contributions.length === 0 ? (
          <div className={styles.empty}>No contributions found</div>
        ) : (
          <div className={styles.grid}>
            {contributions.map((item) => (
              <div key={item.id} className={styles.card}>
                <img 
                  src={`http://localhost:5000/${item.image_path}`} 
                  alt={`Contribution ${item.id}`}
                  className={styles.image}
                />
                <div className={styles.cardContent}>
                  <div className={styles.captionBox}>
                    <h3>User Caption:</h3>
                    <p>{item.user_caption || "No user caption provided"}</p>
                  </div>
                  <div className={styles.captionBox}>
                    <h3>AI Caption:</h3>
                    <p>{item.ai_caption || "No AI caption available"}</p>
                  </div>
                  <div className={styles.metadata}>
                    <p>ID: {item.image_id}</p>
                    <p>Added: {new Date(item.created_at).toLocaleString()}</p>
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
          Back to Upload
        </button>
      </div>
    </>
  );
} 