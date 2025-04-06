import { useState, useEffect } from 'react';
import { getUserContributions } from '../utils/requestHelper';
import Image from 'next/image';
import styles from '../styles/userProfile.module.css';

// Lấy API_URL từ biến môi trường hoặc giá trị mặc định
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api';
// Xử lý để lấy base URL từ API_URL
const BASE_URL = API_URL.replace(/\/api$/, '');

const UserContributions = () => {
  const [contributions, setContributions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedImage, setSelectedImage] = useState(null);

  console.log('UserContributions component rendering');
  console.log(`Base URL for images: ${BASE_URL}`);

  useEffect(() => {
    const fetchContributions = async () => {
      console.log('Fetching user contributions...');
      try {
        const data = await getUserContributions();
        console.log('User contributions response:', data);
        
        if (data && data.contributions) {
          console.log(`Setting ${data.contributions.length} contributions`);
          setContributions(data.contributions);
        } else {
          console.log('No contributions data found:', data);
          setContributions([]);
        }
        
        setLoading(false);
      } catch (err) {
        console.error('Error fetching contributions:', err);
        setError('Không thể tải đóng góp của bạn. Vui lòng thử lại sau.');
        setLoading(false);
      }
    };

    fetchContributions();
  }, []);

  const handleImageClick = (contribution) => {
    console.log('Image clicked:', contribution);
    setSelectedImage(contribution);
  };

  const closeModal = () => {
    setSelectedImage(null);
  };

  if (loading) {
    return <div className={styles.loading}>Đang tải...</div>;
  }

  if (error) {
    return <div className={styles.error}>{error}</div>;
  }

  console.log(`Rendering ${contributions.length} contributions`);

  return (
    <div className={styles.contributionsContainer}>
      <h2 className={styles.sectionTitle}>Đóng góp của tôi</h2>
      
      {contributions.length === 0 ? (
        <div className={styles.emptyState}>
          <p>Bạn chưa có đóng góp nào.</p>
          <p>Bạn có thể đóng góp bằng cách tải lên ảnh và mô tả.</p>
        </div>
      ) : (
        <div className={styles.contributionsGrid}>
          {contributions.map((item, index) => {
            const imagePath = item.image_path || '';
            const fullImageUrl = `${BASE_URL}/uploads/${imagePath}`;
            console.log(`Image ${index+1} path: ${imagePath}`);
            console.log(`Full image URL: ${fullImageUrl}`);
            
            return (
              <div key={item.id || index} className={styles.contributionItem}>
                <div className={styles.imageContainer}>
                  <Image 
                    src={fullImageUrl}
                    alt={item.user_caption || 'Hình ảnh đóng góp'}
                    width={200}
                    height={200}
                    style={{ objectFit: 'cover', cursor: 'pointer' }}
                    onClick={() => handleImageClick(item)}
                    onError={(e) => {
                      console.error(`Image load error for: ${fullImageUrl}`);
                      e.target.src = '/placeholder.png';
                    }}
                  />
                </div>
                <div className={styles.captionText}>
                  <p className={styles.userCaption}>{item.user_caption || 'Không có mô tả'}</p>
                  <p className={styles.modelCaption}>
                    <strong>AI:</strong> {item.model_caption || 'Chưa có nhận diện'}
                  </p>
                  <p className={styles.date}>
                    {new Date(item.created_at).toLocaleDateString('vi-VN')}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {selectedImage && (
        <div className={styles.modal} onClick={closeModal}>
          <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
            <span className={styles.closeButton} onClick={closeModal}>&times;</span>
            <div className={styles.modalImageContainer}>
              <Image 
                src={`${BASE_URL}/uploads/${selectedImage.image_path}`}
                alt={selectedImage.user_caption || 'Hình ảnh đóng góp'}
                width={600}
                height={400}
                style={{ objectFit: 'contain' }}
              />
            </div>
            <div className={styles.modalCaptions}>
              <p><strong>Mô tả của bạn:</strong> {selectedImage.user_caption || 'Không có mô tả'}</p>
              <p><strong>Nhận diện của AI:</strong> {selectedImage.model_caption || 'Chưa có nhận diện'}</p>
              <p><strong>Ngày đóng góp:</strong> {new Date(selectedImage.created_at).toLocaleDateString('vi-VN')}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserContributions; 