import os
from datetime import timedelta

# Đường dẫn tới thư mục static của frontend
FRONTEND_STATIC_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'frontend', 'out'))

# Debug the FRONTEND_STATIC_FOLDER path
print(f"FRONTEND_STATIC_FOLDER path: {FRONTEND_STATIC_FOLDER}")
print(f"Does FRONTEND_STATIC_FOLDER exist? {os.path.exists(FRONTEND_STATIC_FOLDER)}")
if os.path.exists(FRONTEND_STATIC_FOLDER):
    print(f"Contents of FRONTEND_STATIC_FOLDER: {os.listdir(FRONTEND_STATIC_FOLDER)}")

# SECRET_KEY, đảm bảo dài và đủ mạnh (nên đặt trong biến môi trường trong production)
SECRET_KEY = 'hNOg9JHiXCjUcqQzNtvYFKa7eksRLdwSGIfupW5M23T4vPDyZm'
JWT_EXPIRATION_DELTA = timedelta(days=30)  # Token valid for 30 days

# Model paths - Update these to your model paths
MODEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'artifacts'))
print(f"MODEL_PATH path: {MODEL_PATH}")

# Database connection parameters
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_NAME = os.environ.get('DB_NAME', 'image_caption_db')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'postgres')

# Create uploads directory if it doesn't exist
UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'uploads'))
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
CLOUD_RUN_SERVICE_ACCOUNT = "storage-accessor@vietnamese-image-captioning.iam.gserviceaccount.com"

# Google Cloud Storage configuration
GCS_ENABLED = True  # Bật/tắt tính năng sử dụng Google Cloud Storage
GCS_BUCKET_NAME = "vic-storage"  # Tên bucket đã tạo trước đó

# Danh sách các domain được phép CORS
ALLOWED_ORIGINS = [
    # Local development
    'http://localhost:3000',
    'http://localhost:5173',
    'http://localhost:5174',
    'http://192.168.1.14:5173',
    
    # Production domains
    'https://vic.phambatrong.com', 
    'http://vic.phambatrong.com',
    'https://phambatrong.com',
    'http://phambatrong.com',

    # Firebase domains
    'https://vietnamese-image-captioning.web.app',
    'https://vietnamese-image-captioning.firebaseapp.com',
]



