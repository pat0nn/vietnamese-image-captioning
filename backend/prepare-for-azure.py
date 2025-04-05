"""
Các điều chỉnh cần thực hiện trong app.py để chạy trên Azure ML:

1. Thêm imports cho environment variables:
```python
import os
from os import environ
```

2. Thay thế cấu hình cố định bằng environment variables:
```python
# Database connection parameters from environment variables
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_NAME = os.environ.get('DB_NAME', 'image_caption_db')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'postgres')

# Cấu hình security
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-dev-key-replace-in-production')
```

3. Thêm healthcheck endpoint:
```python
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0'
    })
```

4. Thay đổi cách xử lý đường dẫn uploads:
```python
# Create uploads directory if it doesn't exist
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
```

5. Thay đổi cách cấu hình CORS:
```python
# Cấu hình CORS với whitelist từ biến môi trường
allowed_origins = os.environ.get('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
CORS(app, resources={r"/api/*": {"origins": allowed_origins, "supports_credentials": True}})
```

6. Thay đổi main method để chạy từ Azure ML:
```python
if __name__ == "__main__":
    # Khởi tạo database
    init_db()
    
    # Load model khi ứng dụng khởi động
    initialize_model()
    
    # Lấy port từ biến môi trường hoặc sử dụng 5000 mặc định
    port = int(os.environ.get('PORT', 5000))
    
    # Sử dụng host '0.0.0.0' để cho phép truy cập từ bên ngoài container
    app.run(host='0.0.0.0', port=port)
```
""" 