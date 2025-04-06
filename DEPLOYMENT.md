# Hướng dẫn triển khai Vietnamese Image Captioning

Dự án này được triển khai với phần frontend trên Azure Static Web Apps và phần backend chạy local thông qua ngrok.

## Chuẩn bị

1. Cài đặt ngrok: [https://ngrok.com/download](https://ngrok.com/download)
2. Đăng ký tài khoản Azure nếu chưa có
3. Cài đặt GitHub CLI hoặc sử dụng GitHub web interface

## Triển khai Backend (Chạy local với ngrok)

1. Cài đặt các dependencies cho backend:
   ```bash
   cd vietnamese-image-captioning/backend
   pip install -r requirements.txt
   ```

2. Đảm bảo cơ sở dữ liệu PostgreSQL đã được cài đặt và cấu hình đúng trong file `app.py`

3. Chạy backend với ngrok:
   ```bash
   cd vietnamese-image-captioning/backend
   ./run_with_ngrok.sh
   ```

4. Ngrok sẽ tạo một URL public (ví dụ: `https://xxxx-xxxx-xxxx.ngrok.io`). Lưu lại URL này để sử dụng cho frontend.

## Triển khai Frontend (Azure Static Web Apps)

### Tùy chọn 1: Sử dụng Azure Portal

1. Đăng nhập vào Azure Portal và tạo một Static Web App mới
2. Liên kết với repository GitHub của bạn
3. Cấu hình triển khai:
   - App location: `/frontend`
   - Api location: (để trống)
   - Output location: `out`
   - Build command: `npm run build && npm run export`

4. Sau khi triển khai, cấu hình biến môi trường trong Azure Static Web App:
   - Thêm biến môi trường `NEXT_PUBLIC_API_URL` với giá trị là URL ngrok của backend (ví dụ: `https://xxxx-xxxx-xxxx.ngrok.io/api`)

### Tùy chọn 2: Sử dụng GitHub Actions

1. Fork repository này vào GitHub của bạn
2. Tạo một Azure Static Web App mới từ Azure Portal
3. Trong quá trình tạo, liên kết với repository GitHub đã fork
4. Azure sẽ tự động tạo workflow file và thêm secret vào GitHub repository
5. Cấu hình biến môi trường trong Azure Portal:
   - Thêm biến môi trường `NEXT_PUBLIC_API_URL` với giá trị là URL ngrok của backend

## Kiểm tra kết nối

1. Truy cập ứng dụng frontend qua URL Azure Static Web App đã cung cấp
2. Đảm bảo backend đang chạy với ngrok
3. Kiểm tra các chức năng: đăng ký, đăng nhập, upload ảnh và caption

## Lưu ý quan trọng

1. **Mỗi lần khởi động lại ngrok, URL sẽ thay đổi**. Bạn cần cập nhật biến môi trường `NEXT_PUBLIC_API_URL` trong Azure Static Web App.
2. Nếu sử dụng ngrok miễn phí, session sẽ hết hạn sau 2 giờ, bạn cần khởi động lại và cập nhật URL.
3. Trong môi trường production thực tế, nên triển khai backend trên một dịch vụ cloud thay vì sử dụng ngrok.
4. File `staticwebapp.config.json` đã được cấu hình để cho phép CORS từ các URL ngrok, nếu cần thêm domains khác, hãy cập nhật file này.

## Khắc phục sự cố

1. **Lỗi CORS**: Kiểm tra file `staticwebapp.config.json` và cấu hình CORS trong `app.py`
2. **Lỗi kết nối API**: Đảm bảo URL ngrok đúng và backend đang chạy
3. **Lỗi đăng nhập/đăng ký**: Kiểm tra kết nối database và cấu hình backend 