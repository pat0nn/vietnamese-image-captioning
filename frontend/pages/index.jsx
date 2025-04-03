import Image from 'next/image'
import style from '../styles/index.module.css';
import mainImage from "../public/images/image.svg";
import Head from 'next/head';
import { useRef, useState } from 'react';

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
    setClientError("Only one file can be uploaded. Upload a single image.");
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
      setClientError("Please upload an image.");
      return;
    }

    if (!imageFile.type.startsWith("image/")) {
      setClientError("Only image files can be uploaded. Upload a valid file.");
      return;
    }

    if (imageFile.size > 1024 * 1024) {
      setClientError("Only image files 1MB or smaller can be uploaded.");
      return;
    }

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
      
      const response = await fetch('http://localhost:5000/api/caption', {
        method: 'POST',
        body: formData,
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to get image caption');
      }
      
      setImageCaption(data.caption);
    } catch (error) {
      console.error('Error getting caption:', error);
      setClientError(error.message || 'Failed to get image caption');
    } finally {
      setIsLoading(false);
    }
  };

  let toggleContributionMode = () => {
    setIsContributing(!isContributing);
    setUserCaption("");
    setContributionSuccess(false);
  };

  let handleSaveContribution = async () => {
    if (!selectedFile) {
      setClientError("Please upload an image first.");
      return;
    }

    if (!userCaption.trim()) {
      setClientError("Please enter a caption for the image.");
      return;
    }

    setIsSaving(true);
    setClientError("");

    try {
      const formData = new FormData();
      formData.append('image', selectedFile);
      formData.append('userCaption', userCaption);

      const response = await fetch('http://localhost:5000/api/contribute', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to save contribution');
      }

      setContributionSuccess(true);
      setUserCaption("");
    } catch (error) {
      console.error('Error saving contribution:', error);
      setClientError(error.message || 'Failed to save contribution');
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
        <title>Image Captioning App</title>
      </Head>
      <main className={style.container}>
        <h1>Upload your image</h1>
        <div className={style.fileClarifications}>
          <h2>File should be a valid image</h2>
          <span>JPEG, JPG, PNG, SVG or GIF</span>
        </div>

        <button 
          className={style.modeToggleButton} 
          onClick={toggleContributionMode}
        >
          {isContributing ? "Switch to AI Caption Mode" : "Switch to Contribution Mode"}
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
              alt="Preview Image"
              layout="intrinsic"
              width={500}
              height={500} 
            />
          ) : (
            <>
              <Image
                src={mainImage}
                alt="Drag and drop your image here to upload it"
                priority
                ref={zoneImage}
              />
              <p ref={zoneText}>
                {dragging ? "Drop to upload your image" : "Drag & drop your image here"}
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
            Generating caption...
          </div>
        )}
        
        {!isContributing && imageCaption && (
          <div className={style.captionContainer}>
            <h3>Generated Caption:</h3>
            <p className={style.captionText}>{imageCaption}</p>
          </div>
        )}

        {isContributing && previewImage && (
          <div className={style.contributionContainer}>
            <h3>Enter Your Caption:</h3>
            <textarea 
              className={style.captionInput} 
              value={userCaption}
              onChange={(e) => setUserCaption(e.target.value)}
              placeholder="Enter a detailed caption for this image..."
              rows={4}
            />
            <button 
              className={style.saveButton}
              onClick={handleSaveContribution}
              disabled={isSaving}
            >
              {isSaving ? "Saving..." : "Save Contribution"}
            </button>

            {contributionSuccess && (
              <div className={style.successMessage}>
                Thank you for your contribution!
              </div>
            )}
          </div>
        )}
      </main>
    </>
  );
}
