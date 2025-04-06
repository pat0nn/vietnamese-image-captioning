# Hướng dẫn triển khai Vietnamese Image Captioning

Dự án này được triển khai với phần frontend trên Azure Static Web Apps và phần backend chạy local thông qua ngrok.

## Cập nhật quan trọng về xác thực

Hệ thống xác thực đã được cập nhật để sử dụng JWT (JSON Web Token) thông qua Authorization Header thay vì sử dụng cookies. Điều này giúp tránh các vấn đề CORS khi triển khai frontend và backend trên các domain khác nhau.

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

4. Ngrok sẽ tạo một URL public (ví dụ: `https://xxxx-xxxx-xxxx.ngrok-free.app`). **LƯU Ý**: URL ngrok mới sử dụng domain `.ngrok-free.app` thay vì `.ngrok.io` như trước đây.

5. Lưu lại URL này để sử dụng cho frontend. URL API sẽ là `https://xxxx-xxxx-xxxx.ngrok-free.app/api`.

## Triển khai Frontend (Azure Static Web Apps)

### Tùy chọn 1: Sử dụng Azure Portal

1. Đăng nhập vào Azure Portal và tạo một Static Web App mới
2. Liên kết với repository GitHub của bạn
3. Cấu hình triển khai:
   - App location: `frontend`
   - Api location: (để trống)
   - Output location: `out`
   - Build command: `npm run build`

4. Sau khi triển khai, cấu hình biến môi trường trong Azure Static Web Apps:
   - Vào trang Azure Static Web Apps > [your-app] > Configuration
   - Thêm biến môi trường `NEXT_PUBLIC_API_URL` với giá trị là URL ngrok của backend (ví dụ: `https://xxxx-xxxx-xxxx.ngrok-free.app/api`)
   - Nhấn Save và chờ ứng dụng được triển khai lại

### Tùy chọn 2: Sử dụng GitHub Actions

1. Fork repository này vào GitHub của bạn
2. Tạo một Azure Static Web App mới từ Azure Portal
3. Trong quá trình tạo, liên kết với repository GitHub đã fork
4. Azure sẽ tự động tạo workflow file `.github/workflows/azure-static-web-apps.yml` và thêm secret `AZURE_STATIC_WEB_APPS_API_TOKEN` vào GitHub repository của bạn
5. Thêm biến môi trường `NEXT_PUBLIC_API_URL` vào GitHub repository secrets:
   - Vào Settings > Secrets and variables > Actions
   - Thêm repository secret mới với tên `NEXT_PUBLIC_API_URL` và giá trị là URL ngrok của backend

## Khắc phục sự cố xác thực

Nếu bạn gặp vấn đề với xác thực:

1. **Kiểm tra JWT trong localStorage**:
   - Mở console của trình duyệt (F12)
   - Nhập: `localStorage.getItem('auth_token')`
   - Nếu không có token hoặc token không hợp lệ, hãy thử đăng nhập lại

2. **Kiểm tra Authorization header**:
   - Sử dụng tab Network trong Developer Tools
   - Tìm các request đến API và kiểm tra header `Authorization`
   - Header phải có định dạng `Bearer your-jwt-token`

3. **Kiểm tra CORS**:
   - Nếu bạn thấy lỗi CORS, đảm bảo URL của Azure Static Web App đã được thêm vào danh sách `ALLOWED_ORIGINS` trong `app.py`

## Khắc phục sự cố Content Security Policy (CSP)

Nếu bạn gặp lỗi CSP (Content-Security-Policy) như sau:
```
Content-Security-Policy: The page's settings blocked the loading of a resource (connect-src) at http://localhost:5000/api/caption
```

Thực hiện các bước sau:

1. **Kiểm tra URL API trong console**:
   - Mở console của trình duyệt (F12)
   - Kiểm tra xem ứng dụng đang sử dụng URL API nào, bạn sẽ thấy dòng log như: `API URL được sử dụng: http://localhost:5000/api`
   - Nếu URL vẫn là localhost, biến môi trường chưa được áp dụng

2. **Cập nhật biến môi trường trong Azure**:
   - Xác nhận rằng bạn đã thiết lập `NEXT_PUBLIC_API_URL` trong Azure Static Web Apps
   - Đảm bảo URL ngrok chính xác, bao gồm cả `/api` ở cuối
   - Sau khi cập nhật, nhấn Save và chờ ứng dụng được triển khai lại

3. **Cập nhật CSP trong `staticwebapp.config.json`**:
   - Nếu bạn tiếp tục gặp lỗi CSP, hãy cập nhật file `staticwebapp.config.json`
   - Đảm bảo phần `content-security-policy` bao gồm tất cả các domain cần thiết

4. **Kiểm tra ngrok tunnel**:
   - Đảm bảo ngrok vẫn đang chạy và tunnel vẫn hoạt động
   - Nếu ngrok đã dừng, bạn cần chạy lại và cập nhật URL trong biến môi trường

## Khắc phục sự cố triển khai

1. **Lỗi "Cannot find module for page"**: 
   - Lỗi này xảy ra khi `exportPathMap` trong `next.config.js` chứa đường dẫn không tồn tại trong thư mục `pages/`
   - Đảm bảo các trang được liệt kê trong `exportPathMap` đều tồn tại trong thư mục `pages/`

2. **Lỗi "Failed to load config"**: 
   - Kiểm tra cú pháp trong `next.config.js`
   - Đảm bảo không có lỗi JavaScript trong file cấu hình

3. **Lỗi CORS**:
   - Nếu bạn gặp lỗi CORS, hãy kiểm tra cấu hình CORS trong `app.py`
   - Đảm bảo `origins` trong cấu hình CORS bao gồm domain của Azure Static Web App

4. **Lỗi Network Error khi gọi API**:
   - Kiểm tra URL API trong console của trình duyệt
   - Đảm bảo ngrok vẫn đang chạy và URL chính xác
   - Thử truy cập trực tiếp URL API trong trình duyệt để kiểm tra kết nối

## Kiểm tra kết nối

1. Truy cập ứng dụng frontend qua URL Azure Static Web App đã cung cấp
2. Mở console của trình duyệt (F12) để xem các log và lỗi
3. Đảm bảo backend đang chạy với ngrok
4. Kiểm tra các chức năng: đăng ký, đăng nhập, upload ảnh và caption

## Lưu ý quan trọng

1. **Mỗi lần khởi động lại ngrok, URL sẽ thay đổi**. Bạn cần cập nhật biến môi trường `NEXT_PUBLIC_API_URL` trong Azure Static Web Apps (hoặc GitHub Secrets nếu sử dụng GitHub Actions).
2. Nếu sử dụng ngrok miễn phí, session sẽ hết hạn sau 2 giờ, bạn cần khởi động lại và cập nhật URL.
3. Trong môi trường production thực tế, nên triển khai backend trên một dịch vụ cloud thay vì sử dụng ngrok.
4. File `staticwebapp.config.json` đã được cấu hình để cho phép CORS từ các URL ngrok, nếu cần thêm domains khác, hãy cập nhật file này. 