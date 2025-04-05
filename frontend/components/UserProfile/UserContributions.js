import { useState, useEffect } from 'react';
import Image from 'next/image';
import { getUserContributions, updateContribution, deleteContribution } from '../../utils/requestHelper';
import styles from '../../styles/userProfile.module.css';

const UserContributions = () => {
  const [contributions, setContributions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editItem, setEditItem] = useState(null);
  const [editedCaption, setEditedCaption] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [fullSizeImage, setFullSizeImage] = useState(null);
  const [validationError, setValidationError] = useState(null);

  // API URL từ biến môi trường hoặc mặc định
  const API_URL = process.env.NEXT_PUBLIC_API_URL 
  ? `${process.env.NEXT_PUBLIC_API_URL}/api` 
  : 'http://localhost:5000/api';


  useEffect(() => {
    fetchUserContributions();
  }, []);

  // Kiểm tra tính hợp lệ của caption
  const validateCaption = (caption) => {
    // Kiểm tra caption trống
    if (!caption || !caption.trim()) {
      return {
        isValid: false,
        error: 'Vui lòng nhập mô tả cho hình ảnh.'
      };
    }

    // Tách caption thành các từ (bỏ qua khoảng trắng liên tiếp)
    const words = caption.trim().split(/\s+/);
    
    // Kiểm tra số lượng từ tối thiểu
    if (words.length < 5) {
      return {
        isValid: false,
        error: 'Mô tả phải có ít nhất 5 từ.'
      };
    }
    
    // Kiểm tra độ dài từng từ
    const longWords = words.filter(word => word.length > 7);
    if (longWords.length > 0) {
      return {
        isValid: false,
        error: `Không được sử dụng từ dài quá 7 ký tự: ${longWords.join(', ')}`
      };
    }
    
    return {
      isValid: true,
      error: null
    };
  };

  const fetchUserContributions = async () => {
    try {
      setLoading(true);
      const response = await getUserContributions();
      setContributions(response.contributions || []);
    } catch (err) {
      console.error('Error fetching contributions:', err);
      setError('Không thể tải danh sách đóng góp. Vui lòng thử lại sau.');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (item) => {
    setEditItem(item);
    setEditedCaption(item.user_caption || '');
    setValidationError(null);
  };

  const handleCancelEdit = () => {
    setEditItem(null);
    setEditedCaption('');
    setValidationError(null);
  };

  const handleSaveEdit = async (imageId) => {
    // Kiểm tra tính hợp lệ của caption
    const validationResult = validateCaption(editedCaption);
    if (!validationResult.isValid) {
      setValidationError(validationResult.error);
      return;
    }

    try {
      setIsSaving(true);
      setValidationError(null);
      await updateContribution(imageId, editedCaption);
      
      // Update the item in the local state
      setContributions(contributions.map(item => 
        item.image_id === imageId 
          ? { ...item, user_caption: editedCaption } 
          : item
      ));
      
      setEditItem(null);
    } catch (err) {
      console.error('Error updating caption:', err);
      setError('Không thể cập nhật mô tả. Vui lòng thử lại sau.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async (imageId) => {
    if (!confirm('Bạn có chắc chắn muốn xóa đóng góp này không?')) {
      return;
    }
    
    try {
      await deleteContribution(imageId);
      
      // Remove the item from the local state
      setContributions(contributions.filter(item => item.image_id !== imageId));
    } catch (err) {
      console.error('Error deleting contribution:', err);
      setError('Không thể xóa đóng góp. Vui lòng thử lại sau.');
    }
  };

  // Tạo URL đầy đủ cho hình ảnh
  const getImageUrl = (imagePath) => {
    // Nếu đường dẫn đã là URL đầy đủ, trả về nó
    if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
      return imagePath;
    }
    // Ngược lại, ghép với API_URL
    return `${API_URL}/uploads/${imagePath}`;
  };

  // Mở ảnh độ phân giải đầy đủ
  const openFullSizeImage = (item) => {
    setFullSizeImage({
      src: getImageUrl(item.image_path),
      alt: item.user_caption || 'Hình ảnh đóng góp',
      caption: item.user_caption || 'Không có mô tả'
    });
  };

  // Đóng ảnh độ phân giải đầy đủ
  const closeFullSizeImage = () => {
    setFullSizeImage(null);
  };

  // Ngăn sự kiện lan truyền khi click vào modal nội dung (chỉ đóng khi click vào nền)
  const handleModalContentClick = (e) => {
    e.stopPropagation();
  };

  if (loading) {
    return <div className={styles.loading}>Đang tải đóng góp của bạn...</div>;
  }

  if (error) {
    return <div className={styles.error}>{error}</div>;
  }

  if (!contributions.length) {
    return <div className={styles.empty}>Bạn chưa có đóng góp nào.</div>;
  }

  return (
    <div className={styles.contributionsContainer}>
      <h2>Các đóng góp của bạn</h2>
      
      {contributions.map((item) => (
        <div key={item.image_id} className={styles.contributionItem}>
          <div 
            className={styles.contributionImage}
            onClick={() => openFullSizeImage(item)}
          >
            {/* Sử dụng thẻ img thông thường thay vì Next.js Image */}
            <img 
              src={getImageUrl(item.image_path)}
              alt={item.user_caption || 'Hình ảnh đóng góp'}
              width={200}
              height={200}
              style={{ objectFit: 'cover', cursor: 'pointer' }}
              className={styles.imagePreview}
            />
          </div>
          
          <div className={styles.contributionDetails}>
            {editItem && editItem.image_id === item.image_id ? (
              <div className={styles.editForm}>
                <textarea
                  value={editedCaption}
                  onChange={(e) => setEditedCaption(e.target.value)}
                  className={styles.editInput}
                  placeholder="Nhập mô tả mới cho hình ảnh này..."
                  rows={4}
                />
                {validationError && (
                  <div className={styles.validationError}>
                    {validationError}
                  </div>
                )}
                <div className={styles.editActions}>
                  <button 
                    onClick={() => handleSaveEdit(item.image_id)}
                    className={styles.saveButton}
                    disabled={isSaving}
                  >
                    {isSaving ? 'Đang lưu...' : 'Lưu'}
                  </button>
                  <button 
                    onClick={handleCancelEdit}
                    className={styles.cancelButton}
                  >
                    Hủy
                  </button>
                </div>
              </div>
            ) : (
              <>
                <div className={styles.captionBox}>
                  <h3>Mô tả của bạn:</h3>
                  <p>{item.user_caption || "Không có mô tả"}</p>
                </div>
                {item.ai_caption && (
                  <div className={styles.captionBox}>
                    <h3>Mô tả AI:</h3>
                    <p>{item.ai_caption}</p>
                  </div>
                )}
                <div className={styles.metadata}>
                  <p>Thời gian: {new Date(item.created_at).toLocaleString()}</p>
                </div>
                <div className={styles.itemActions}>
                  <button 
                    onClick={() => handleEdit(item)}
                    className={styles.editButton}
                  >
                    Sửa mô tả
                  </button>
                  <button 
                    onClick={() => handleDelete(item.image_id)}
                    className={styles.deleteButton}
                  >
                    Xóa đóng góp
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      ))}

      {/* Modal hiển thị ảnh độ phân giải đầy đủ */}
      {fullSizeImage && (
        <div className={styles.imageModal} onClick={closeFullSizeImage}>
          <div className={styles.modalContent} onClick={handleModalContentClick}>
            <button className={styles.closeButton} onClick={closeFullSizeImage}>×</button>
            <div className={styles.fullSizeImageContainer}>
              <img 
                src={fullSizeImage.src} 
                alt={fullSizeImage.alt} 
                className={styles.fullSizeImage}
              />
            </div>
            <div className={styles.modalCaption}>
              <h3>Mô tả:</h3>
              <p>{fullSizeImage.caption}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserContributions; 