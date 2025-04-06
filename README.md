# Vietnamese Image Captioning

Hệ thống tạo chú thích cho hình ảnh bằng tiếng Việt với Frontend được triển khai trên Azure Static Web App và Backend chạy cục bộ trên máy tính cá nhân thông qua ngrok tunnel.

## Cách triển khai

### 1. Chuẩn bị Backend

1. Cài đặt dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. Chạy backend với ngrok tunnel để có thể truy cập từ internet:
   ```bash
   cd backend
   python run_with_tunnel.py
   ```
   
   **Lưu ý quan trọng**: 
   - Nếu bạn có tài khoản ngrok, hãy thêm auth token vào biến `NGROK_AUTH_TOKEN` trong file `run_with_tunnel.py` để có địa chỉ ổn định hơn và kéo dài thời gian kết nối.
   - Ngrok free chỉ cho phép session kéo dài 2 giờ, sau đó bạn cần khởi động lại.
   - Khi script chạy, nó sẽ tự động tạo file `.env.local` trong thư mục frontend với các biến môi trường cần thiết.

3. Lưu URL ngrok hiển thị trong terminal. Sẽ có dạng `https://xxxx-xxxx-xxxx-xxxx.ngrok-free.app`

### 2. Triển khai Frontend lên Azure Static Web App

1. Trước khi build và deploy, cập nhật biến môi trường trong Azure Static Web App với thông tin từ ngrok tunnel:
   - `NEXT_PUBLIC_API_URL`: URL ngrok của backend + `/api` (ví dụ: `https://xxxx-xxxx-xxxx-xxxx.ngrok-free.app/api`)
   - `NEXT_PUBLIC_BACKEND_HOST`: Domain của ngrok (ví dụ: `xxxx-xxxx-xxxx-xxxx.ngrok-free.app`) không bao gồm giao thức http/https
   - `NEXT_PUBLIC_BACKEND_PORT`: Để trống (khi sử dụng ngrok)
   
2. Build frontend:
   ```bash
   cd frontend
   npm install
   npm run build
   ```

3. Deploy lên Azure Static Web App qua Azure Portal hoặc GitHub Actions:
   - Trên Azure Portal: Tạo mới Static Web App và upload thư mục build
   - Với GitHub: Tạo workflow để tự động deploy khi push lên GitHub

### 3. Test cục bộ trước khi deploy

1. Khởi động backend với ngrok tunnel:
   ```bash
   cd backend
   python run_with_tunnel.py
   ```

2. Trong terminal khác, khởi động frontend dev server:
   ```bash
   cd frontend
   npm run dev
   ```

3. Frontend cục bộ sẽ sử dụng biến môi trường trong file `.env.local` (được tạo tự động bởi script run_with_tunnel.py) để kết nối với backend qua ngrok.

## Xử lý CORS và Authentication

Hệ thống đã được cấu hình để xử lý CORS và token authentication giữa frontend trên Azure và backend local:

1. **CORS**: Backend được cấu hình để chấp nhận request từ bất kỳ origin nào và hỗ trợ credentials.
2. **Token Authentication**: 
   - Tokens được lưu trong localStorage và cookies trên frontend
   - Cookies được cấu hình với `SameSite=None` và `Secure=true` để hoạt động tốt với cross-origin requests
   - Backend luôn kiểm tra token trong header và cookies

## Lưu ý và Xử lý lỗi

1. **URL ngrok thay đổi**:
   - Mỗi khi khởi động lại ngrok, URL sẽ thay đổi (trừ khi bạn sử dụng tài khoản Pro của ngrok)
   - Sau mỗi lần URL ngrok thay đổi, bạn cần cập nhật lại biến môi trường trong Azure Static Web App và redeploy frontend

2. **Vấn đề với cookie**:
   - Nếu gặp lỗi authentication, kiểm tra console của trình duyệt để xem có lỗi CORS liên quan đến cookies không
   - Có thể cần tắt tính năng chặn cookies bên thứ ba trong trình duyệt hoặc cấu hình SameSite

3. **HTTPS và HTTP**:
   - Ngrok luôn sử dụng HTTPS, trong khi local frontend có thể chạy trên HTTP
   - Điều này có thể gây ra vấn đề với cookie secure, hãy kiểm tra console của browser

4. **Thời gian sống của ngrok**:
   - Phiên ngrok miễn phí chỉ kéo dài tối đa 2 giờ
   - Nếu bạn cần thời gian dài hơn, hãy đăng ký tài khoản ngrok hoặc xem xét giải pháp khác như cloudflared

5. **Giải pháp thay thế**:
   - Thay vì ngrok, bạn cũng có thể sử dụng port forwarding trên router nếu có địa chỉ IP tĩnh
   - Cloudflared cũng là một giải pháp tunnel tương tự ngrok nhưng có chính sách khác

## Cấu trúc thư mục

- `backend/`: API server Flask
  - `app.py`: Ứng dụng Flask chính
  - `run_with_tunnel.py`: Script chạy backend với ngrok tunnel
  - `requirements.txt`: Dependencies Python
  - `uploads/`: Thư mục lưu trữ hình ảnh được tải lên

- `frontend/`: Ứng dụng Next.js
  - `next.config.js`: Cấu hình Next.js với hỗ trợ domain của ngrok
  - `staticwebapp.config.json`: Cấu hình Azure Static Web App
  - `.env.local`: Biến môi trường local (được tạo tự động bởi `run_with_tunnel.py`)
  - `utils/`: Thư mục chứa các utility function và API clients
