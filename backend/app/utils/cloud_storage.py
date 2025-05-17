import os
import io
from google.cloud import storage
from PIL import Image
import uuid
from flask import url_for
import logging
from app.config.settings import GCS_BUCKET_NAME, CLOUD_RUN_SERVICE_ACCOUNT




# Khởi tạo client
def get_storage_client():
    """Trả về Google Cloud Storage client đã được xác thực"""
    try:
        return storage.Client()
    except Exception as e:
        logging.error(f"Error initializing Google Cloud Storage client: {str(e)}")
        raise

def upload_image(image_data, filename=None, folder=None):
    """
    Upload hình ảnh lên Google Cloud Storage
    
    Args:
        image_data: Dữ liệu hình ảnh (PIL Image hoặc bytes)
        filename: Tên file tùy chọn (nếu không cung cấp sẽ tạo UUID)
        folder: Thư mục con tùy chọn trên bucket
        
    Returns:
        tuple: (image_id, gcs_path, public_url)
    """
    try:
        # Tạo tên file nếu không được cung cấp
        if not filename:
            image_id = str(uuid.uuid4())
            filename = f"{image_id}.jpg"
        else:
            # Lấy image_id từ filename nếu có định dạng uuid_filename.jpg
            try:
                image_id = filename.split('_')[0]
            except:
                image_id = os.path.splitext(filename)[0]
        
        # Tạo đường dẫn đầy đủ trên GCS
        gcs_path = filename
        if folder:
            gcs_path = f"{folder}/{filename}"
        
        # Khởi tạo client và bucket
        client = get_storage_client()
        bucket = client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(gcs_path)
        
        # Xử lý dữ liệu hình ảnh
        if isinstance(image_data, Image.Image):
            # Convert PIL Image sang bytes với EXIF orientation đã được chuẩn hóa
            img_byte_arr = io.BytesIO()
            
            # Check if image has EXIF data
            exif_bytes = None
            try:
                import piexif
                if hasattr(image_data, '_getexif') and image_data._getexif() is not None:
                    # Convert EXIF data to bytes
                    exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
                    
                    # Copy all EXIF data except orientation
                    for tag, value in image_data._getexif().items():
                        # Skip the orientation tag (274)
                        if tag == 274:
                            continue
                        
                        # Find which IFD this tag belongs to
                        ifd = "0th"
                        if tag in piexif.ExifIFD.__dict__.values():
                            ifd = "Exif"
                        elif tag in piexif.GPSIFD.__dict__.values():
                            ifd = "GPS"
                        
                        # Add the tag to the appropriate IFD
                        if isinstance(value, bytes):
                            exif_dict[ifd][tag] = value
                        else:
                            try:
                                # Try to convert the value to bytes if needed
                                exif_dict[ifd][tag] = value
                            except:
                                # Skip tags that can't be converted
                                pass
                    
                    # Set orientation to normal (1)
                    exif_dict["0th"][274] = 1
                    
                    # Convert to bytes
                    try:
                        exif_bytes = piexif.dump(exif_dict)
                    except Exception as exif_error:
                        logging.warning(f"Error dumping EXIF data: {str(exif_error)}")
                        exif_bytes = None
            except ImportError:
                logging.warning("piexif module not available, saving without EXIF data")
                exif_bytes = None
            except Exception as e:
                logging.warning(f"Error processing EXIF data: {str(e)}")
                exif_bytes = None
                
            # Save the image with normalized orientation
            if exif_bytes:
                image_data.save(img_byte_arr, format='JPEG', exif=exif_bytes, quality=95)
            else:
                image_data.save(img_byte_arr, format='JPEG', quality=95)
                
            img_byte_arr.seek(0)
            blob.upload_from_file(img_byte_arr, content_type='image/jpeg')
        elif isinstance(image_data, bytes):
            # Upload trực tiếp từ bytes
            blob.upload_from_string(image_data, content_type='image/jpeg')
        else:
            raise ValueError("image_data phải là PIL Image hoặc bytes")
        
        # Lấy public URL
        public_url = f"gs://{GCS_BUCKET_NAME}/{gcs_path}"
        
        return image_id, gcs_path, public_url
    
    except Exception as e:
        logging.error(f"Error uploading image to GCS: {str(e)}")
        raise

def delete_image(gcs_path):
    """
    Xóa hình ảnh từ Google Cloud Storage
    
    Args:
        gcs_path: Đường dẫn đầy đủ tới file trên GCS
        
    Returns:
        bool: True nếu xóa thành công
    """
    try:
        client = get_storage_client()
        bucket = client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(gcs_path)
        
        # Kiểm tra xem file có tồn tại không
        if blob.exists():
            blob.delete()
            return True
        else:
            logging.warning(f"File {gcs_path} not found in bucket {GCS_BUCKET_NAME}")
            return False
            
    except Exception as e:
        logging.error(f"Error deleting image from GCS: {str(e)}")
        raise

def get_image_url(gcs_path):
    """
    Tạo URL truy cập công khai cho file GCS
    
    Args:
        gcs_path: Đường dẫn file trên GCS
        
    Returns:
        str: URL công khai cho file
    """
    try:
        client = get_storage_client()
        bucket = client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(gcs_path)
        
        # Tạo URL có thời hạn (signed URL) cho phép truy cập trong 1 giờ
        try:
            # Thử tạo signed URL với service account (cho môi trường local)
            url = blob.generate_signed_url(
                version="v4",
                expiration=3600,  # 1 giờ
                method="GET",
                service_account_email=CLOUD_RUN_SERVICE_ACCOUNT,
            )
        except Exception as e:
            # Nếu không có khóa private (trên Cloud Run), tạo URL mà không cần service_account_email
            logging.info(f"Falling back to default credentials for signed URL: {str(e)}")
            url = blob.generate_signed_url(
                version="v4",
                expiration=3600,  # 1 giờ
                method="GET"
            )
        
        return url
    
    except Exception as e:
        logging.error(f"Error generating signed URL: {str(e)}")
        raise

def download_image(gcs_path):
    """
    Tải hình ảnh từ Google Cloud Storage
    
    Args:
        gcs_path: Đường dẫn file trên GCS
        
    Returns:
        bytes: Dữ liệu hình ảnh
    """
    try:
        client = get_storage_client()
        bucket = client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(gcs_path)
        
        # Tải xuống dữ liệu
        content = blob.download_as_bytes()
        return content
    
    except Exception as e:
        logging.error(f"Error downloading image from GCS: {str(e)}")
        raise

def list_images(prefix=None):
    """
    Liệt kê tất cả các hình ảnh trong bucket
    
    Args:
        prefix: Tiền tố đường dẫn để lọc (tùy chọn)
        
    Returns:
        list: Danh sách các đường dẫn file
    """
    try:
        client = get_storage_client()
        bucket = client.bucket(GCS_BUCKET_NAME)
        
        blobs = bucket.list_blobs(prefix=prefix)
        return [blob.name for blob in blobs]
    
    except Exception as e:
        logging.error(f"Error listing images from GCS: {str(e)}")
        raise 