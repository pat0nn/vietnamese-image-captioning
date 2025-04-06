# Vietnamese Image Captioning - Backend

Backend API cho dự án Vietnamese Image Captioning sử dụng Flask.

## Kiến trúc triển khai

- **Backend**: Chạy ở local, truy cập qua ngrok tunnel
- **Frontend**: Triển khai trên Azure Static Web Apps
- **Kết nối**: Frontend truy cập backend thông qua proxy của Azure Static Web Apps

## Cài đặt

1. Cài đặt các package cần thiết:

```bash
pip install -r requirements.txt
```

2. Cài đặt ngrok:

```bash
pip install pyngrok
# hoặc tải từ https://ngrok.com/download
```

## Cấu hình ngrok

1. Đăng ký tài khoản tại [ngrok.com](https://ngrok.com) nếu chưa có
2. Lấy authtoken từ [dashboard ngrok](https://dashboard.ngrok.com/get-started/your-authtoken)
3. Cập nhật file `ngrok.yml` với authtoken của bạn:

```yaml
authtoken: YOUR_NGROK_AUTH_TOKEN
```

## Chạy Backend Server

1. Khởi động Flask server:

```bash
python app.py
```

2. Trong một terminal khác, chạy ngrok để tạo tunnel đến backend:

```bash
# Cách 1: Sử dụng file cấu hình
ngrok start --config ngrok.yml backend

# Cách 2: Chạy lệnh trực tiếp
ngrok http 5000
```

3. Sau khi chạy ngrok, bạn sẽ nhận được URL tunnel (ví dụ: https://7e6a-116-96-47-45.ngrok-free.app)

## Cập nhật cấu hình proxy trong Frontend

Khi URL ngrok thay đổi (sau mỗi 2 giờ hoặc khi bạn khởi động lại ngrok), bạn cần cập nhật:

1. Mở file `frontend/staticwebapp.config.json`
2. Cập nhật URL ngrok trong phần routes:

```json
{
  "routes": [
    {
      "route": "/api/*",
      "rewrite": "https://NEW-NGROK-URL.ngrok-free.app/api/:splat"
    },
    {
      "route": "/uploads/*",
      "rewrite": "https://NEW-NGROK-URL.ngrok-free.app/uploads/:splat"
    }
  ]
}
```

3. Build và deploy lại frontend

## Cấu hình Database

Backend sử dụng PostgreSQL. Đảm bảo bạn đã cài đặt và cấu hình PostgreSQL:

```python
# Các tham số kết nối trong app.py
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'image_caption_db'
DB_USER = 'postgres'
DB_PASSWORD = 'postgres'
```

## Đường dẫn API

- `/api/register` - Đăng ký người dùng mới
- `/api/login` - Đăng nhập
- `/api/logout` - Đăng xuất
- `/api/user` - Lấy thông tin người dùng hiện tại
- `/api/caption` - Tạo caption cho ảnh
- `/api/contribute` - Đóng góp ảnh và caption
- `/api/contributions` - Lấy danh sách các đóng góp
- `/api/user/contributions` - Lấy danh sách đóng góp của người dùng hiện tại
- `/api/contribution/<image_id>` - Cập nhật hoặc xóa đóng góp

## Lưu ý về CORS

Backend được cấu hình để chấp nhận request từ:
- http://localhost:3000 (Môi trường phát triển)
- https://ashy-ocean-0e5aab200.6.azurestaticapps.net (Frontend được triển khai)

Frontend sử dụng proxy từ Azure Static Web Apps để chuyển tiếp request đến backend, giúp tránh các vấn đề CORS. 