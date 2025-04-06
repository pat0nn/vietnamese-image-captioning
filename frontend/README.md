# Vietnamese Image Captioning - Frontend

Ứng dụng frontend cho dự án Vietnamese Image Captioning. Sử dụng Next.js và được triển khai trên Azure Static Web Apps kết nối với backend qua proxy.

## Cấu trúc Triển khai

- **Frontend**: Được triển khai trên Azure Static Web Apps
- **Backend**: Chạy ở local, kết nối thông qua ngrok tunnel
- **API Proxy**: Azure Static Web Apps cung cấp tính năng proxy để chuyển tiếp yêu cầu API, tránh vấn đề CORS

## Yêu cầu

- Node.js (phiên bản 14 trở lên)
- npm hoặc yarn
- Azure CLI
- Azure Static Web Apps CLI (swa-cli)
- Ngrok

## Cài đặt

1. Cài đặt dependencies:

```bash
yarn install
# hoặc
npm install
```

2. Cài đặt Azure Static Web Apps CLI:

```bash
npm install -g @azure/static-web-apps-cli
```

3. Cài đặt ngrok:

```bash
npm install -g ngrok
# hoặc tải từ https://ngrok.com/download
```

## Cập nhật URL Ngrok

Khi ngrok tunnel thay đổi (sau mỗi 2 giờ), bạn cần cập nhật URL trong cấu hình proxy:

1. Mở file `staticwebapp.config.json`
2. Cập nhật URL ngrok trong phần routes:

```json
{
  "routes": [
    {
      "route": "/api/*",
      "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
      "rewrite": "https://NEW-NGROK-URL.ngrok-free.app/api/:splat"
    },
    {
      "route": "/uploads/*",
      "methods": ["GET"],
      "rewrite": "https://NEW-NGROK-URL.ngrok-free.app/uploads/:splat"
    }
  ]
}
```

3. Build và deploy lại ứng dụng

## Cách thức hoạt động của proxy

Azure Static Web Apps cung cấp tính năng proxy cho phép:

1. Frontend gửi request đến `/api/*` (cùng domain)
2. Azure sẽ chuyển tiếp request đến backend ngrok theo cấu hình `rewrite`
3. Tương tự, request cho hình ảnh qua đường dẫn `/uploads/*` cũng được chuyển tiếp

Ưu điểm của cách tiếp cận này:
- **Không có vấn đề CORS**: Vì browser coi mọi request là đến cùng origin (same-origin)
- **Tính bảo mật cao**: Headers được bảo toàn qua proxy
- **Không cần cấu hình phức tạp**: Không cần thay đổi cấu hình CORS ở backend

## Chạy Backend với Ngrok

1. Khởi động backend server ở local:

```bash
cd ../backend
python app.py
```

2. Mở terminal mới và tạo ngrok tunnel đến backend:

```bash
# Sử dụng file cấu hình
ngrok start --config ngrok.yml backend

# Hoặc lệnh trực tiếp
ngrok http 5000
```

3. Sao chép URL https từ ngrok và cập nhật trong `staticwebapp.config.json`

## Deploy lên Azure Static Web Apps

1. Build và export ứng dụng:

```bash
yarn build-static
# hoặc
npm run build-static
```

2. Deploy lên Azure bằng SWA CLI:

```bash
swa deploy ./out --env production
# hoặc
yarn deploy-azure
```

## Lưu ý Quan Trọng

- Mỗi khi ngrok URL thay đổi, bạn chỉ cần cập nhật URL trong `staticwebapp.config.json` và deploy lại
- Không cần thay đổi code trong ứng dụng vì chúng ta sử dụng đường dẫn tương đối
- Cấu hình CORS không còn cần thiết vì tất cả request đều đi qua proxy

## Cách Sử Dụng Static Web Apps CLI

```bash
# Login vào Azure
az login

# Liệt kê static web apps
az staticwebapp list

# Deploy
swa deploy ./out --env production --app-name YOUR_APP_NAME
``` 