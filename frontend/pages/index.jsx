import Image from 'next/image'
import style from '../styles/index.module.css';
import mainImage from "../public/images/image.svg";
import Head from 'next/head';
import { useRef, useState } from 'react';
import { useAuth } from '../components/Auth/AuthContext';
import AuthNav from '../components/Auth/AuthNav';
import AuthModal from '../components/Auth/AuthModal';
import { getImageCaption, contributeImage } from '../utils/requestHelper';
import { toast } from 'react-toastify';

export default function Home() {
  let fileInputRef = useRef(null);
  let dropzone = useRef(null);
  let zoneImage = useRef(null);
  let zoneText = useRef(null);

  let [clientError, setClientError] = useState("");
  let [dragging, setDragging] = useState(false);
  let [previewImage, setPreviewImage] = useState(null);
  let [isLoading, setIsLoading] = useState(false);
  let [imageCaption, setImageCaption] = useState("");
  let [userCaption, setUserCaption] = useState("");
  let [isSaving, setIsSaving] = useState(false);
  let [isContributing, setIsContributing] = useState(false);
  let [contributionSuccess, setContributionSuccess] = useState(false);
  let [selectedFile, setSelectedFile] = useState(null);
  let [showAuthModal, setShowAuthModal] = useState(false);

  const { isAuthenticated } = useAuth();

  let handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  let handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragging(false);
    let { files } = e.dataTransfer;
    if (files && files.length === 1) {
      handleAddFile(files);
      return;
    }
    setClientError("Chỉ có thể tải lên một tệp. Vui lòng tải lên một hình ảnh duy nhất.");
  };

  let handleDragEnter = (e) => {
    if (e.target === zoneImage.current || e.target === zoneText.current) return;
    e.preventDefault();
    e.stopPropagation();
    setDragging(true);
  };

  let handleDragLeave = (e) => {
    if (e.target === zoneImage.current || e.target === zoneText.current) return;
    e.preventDefault();
    e.stopPropagation();
    setDragging(false);
  };

  let handleAddFile = async (sentFileList) => {
    let imageFile = sentFileList[0];

    if (!imageFile) {
      setClientError("Vui lòng tải lên một hình ảnh.");
      return;
    }

    if (!imageFile.type.startsWith("image/")) {
      setClientError("Chỉ có thể tải lên tệp hình ảnh. Vui lòng tải lên tệp hợp lệ.");
      return;
    }

    // if (imageFile.size > 1024 * 1024) {
    //   setClientError("Chỉ có thể tải lên tệp hình ảnh nhỏ hơn hoặc bằng 1MB.");
    //   return;
    // }

    setSelectedFile(imageFile);
    let imgURL = URL.createObjectURL(imageFile);
    setPreviewImage(imgURL);
    setClientError("");
    setContributionSuccess(false);

    // Send the image to the backend for captioning
    await uploadAndGetCaption(imageFile);
  };

  let uploadAndGetCaption = async (imageFile) => {
    setIsLoading(true);
    setImageCaption("");
    
    try {
      const formData = new FormData();
      formData.append('image', imageFile);
      
      const data = await getImageCaption(formData);
      setImageCaption(data.caption);
    } catch (error) {
      console.error('Error getting caption:', error);
      setClientError(error.message || 'Không thể nhận mô tả hình ảnh');
    } finally {
      setIsLoading(false);
    }
  };

  let toggleContributionMode = () => {
    if (isContributing) {
      // Switching from contribution mode to AI caption mode
      setIsContributing(false);
      setUserCaption("");
      setContributionSuccess(false);
    } else {
      // Switching to contribution mode
      if (!isAuthenticated) {
        // Show login modal if not authenticated
        setShowAuthModal(true);
        return;
      }
      setIsContributing(true);
    }
  };

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

  let handleSaveContribution = async () => {
    if (!selectedFile) {
      setClientError("Vui lòng tải lên hình ảnh trước.");
      return;
    }

    // Kiểm tra tính hợp lệ của caption
    const validationResult = validateCaption(userCaption);
    if (!validationResult.isValid) {
      setClientError(validationResult.error);
      return;
    }

    // Check if user is authenticated
    if (!isAuthenticated) {
      setShowAuthModal(true);
      return;
    }

    setIsSaving(true);
    setClientError("");

    try {
      const formData = new FormData();
      formData.append('image', selectedFile);
      formData.append('userCaption', userCaption);
      formData.append('skipAiCaption', 'true');

      await contributeImage(formData);

      setContributionSuccess(true);
      setUserCaption("");
      toast.success("Đóng góp của bạn đã được lưu thành công!");
    } catch (error) {
      console.error('Error saving contribution:', error);
      setClientError(error.response?.data?.error || 'Không thể lưu đóng góp');
      toast.error("Có lỗi xảy ra khi lưu đóng góp của bạn.");
    } finally {
      setIsSaving(false);
    }
  };

  let clickFileInput = () => {
    fileInputRef.current.click();
  };

  return (
    <>
      <Head>
        <title>Ứng Dụng Mô Tả Hình Ảnh</title>
      </Head>
      <div className={style.navBar}>
        <h1 className={style.logo}>Image Caption</h1>
        <AuthNav />
      </div>
      <main className={style.container}>
        <h1>Tải lên hình ảnh của bạn</h1>
        <div className={style.fileClarifications}>
          <h2>Tệp phải là hình ảnh hợp lệ</h2>
          <span>JPEG, JPG, PNG</span>
        </div>

        <button 
          className={style.modeToggleButton} 
          onClick={toggleContributionMode}
        >
          {isContributing ? "Chuyển sang Chế độ Mô tả AI" : "Chuyển sang Chế độ Đóng góp"}
        </button>

        <section
          className={dragging ? `${style.imageDrop} ${style.activeImageDrop}` : style.imageDrop}
          onClick={clickFileInput}
          ref={dropzone}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          onDragEnter={handleDragEnter}
          onDragLeave={handleDragLeave}
        >
          {previewImage ? (
            <Image
              src={previewImage}
              alt="Xem trước hình ảnh"
              layout="intrinsic"
              width={500}
              height={500} 
            />
          ) : (
            <>
              <Image
                src={mainImage}
                alt="Chọn hình ảnh hoặc kéo-thả vào đây để tải lên"
                priority
                ref={zoneImage}
              />
              <p ref={zoneText}>
                {dragging ? "Thả để tải lên hình ảnh của bạn" : "Chọn hình ảnh hoặc kéo-thả vào đây để tải lên"}
              </p>
            </>
          )}
        </section>

        <input
          type="file"
          name="chooseFile"
          id="chooseFile"
          className={style.fileInput}
          accept="image/*"
          ref={fileInputRef}
          onChange={(e) => handleAddFile(e.target.files)}
        />

        {clientError && <p className={style.errorMessage}>{clientError}</p>}
        
        {isLoading && (
          <div className={style.loadingMessage}>
            Đang tạo mô tả...
          </div>
        )}
        
        {!isContributing && imageCaption && (
          <div className={style.captionContainer}>
            <h3>Mô tả đã tạo:</h3>
            <p className={style.captionText}>{imageCaption}</p>
          </div>
        )}

        {isContributing && previewImage && (
          <div className={style.contributionContainer}>
            <h3>Nhập mô tả của bạn:</h3>
            <textarea 
              className={style.captionInput} 
              value={userCaption}
              onChange={(e) => setUserCaption(e.target.value)}
              placeholder="Nhập mô tả chi tiết cho hình ảnh này..."
              rows={4}
            />
            <button 
              className={style.saveButton}
              onClick={handleSaveContribution}
              disabled={isSaving}
            >
              {isSaving ? "Đang lưu..." : "Lưu đóng góp"}
            </button>

            {contributionSuccess && (
              <div className={style.successMessage}>
                Cảm ơn bạn đã đóng góp!
              </div>
            )}
          </div>
        )}

        {showAuthModal && (
          <AuthModal onClose={() => setShowAuthModal(false)} />
        )}
      </main>
    </>
  );
}
