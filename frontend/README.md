# Vietnamese Image Captioning - Frontend

Ứng dụng frontend cho dự án Vietnamese Image Captioning. Sử dụng Next.js và được triển khai trên Azure Static Web Apps kết nối với backend qua ngrok tunnel.

## Cấu trúc Triển khai

- **Frontend**: Được triển khai trên Azure Static Web Apps
- **Backend**: Chạy ở local, kết nối thông qua ngrok tunnel

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

Khi ngrok tunnel thay đổi (sau mỗi 2 giờ), bạn cần cập nhật URL trong file cấu hình:

1. Mở file `utils/apiConfig.js`
2. Cập nhật giá trị `NGROK_URL` với URL tunnel mới
3. Lưu file và build lại ứng dụng

```javascript
// Ví dụ - cập nhật dòng này:
const NGROK_URL = 'https://new-tunnel-url.ngrok-free.app';
```

## Chạy Backend với Ngrok

1. Khởi động backend server ở local:

```bash
cd ../backend
python app.py
```

2. Mở terminal mới và tạo ngrok tunnel đến backend:

```bash
ngrok http 5000
```

3. Sao chép URL https từ ngrok và cập nhật trong `utils/apiConfig.js`

## Deploy lên Azure Static Web Apps

### Cách 1: Sử dụng GitHub Actions

1. Commit và push code lên GitHub repository
2. Tạo Azure Static Web App từ Azure Portal và kết nối với GitHub repo
3. Azure sẽ tự động deploy khi có commit mới

### Cách 2: Deploy thủ công bằng CLI

1. Cập nhật URL ngrok trong `utils/apiConfig.js`
2. Build và export ứng dụng:

```bash
yarn build-static
# hoặc
npm run build-static
```

3. Deploy lên Azure bằng SWA CLI:

```bash
swa deploy ./out --env production
# hoặc
yarn deploy-azure
```

## Lưu ý Quan Trọng

- Mỗi khi ngrok URL thay đổi (sau 2 giờ), bạn cần cập nhật URL trong `utils/apiConfig.js` và deploy lại frontend
- Đảm bảo backend server luôn chạy khi triển khai frontend
- Nếu gặp vấn đề về CORS, kiểm tra cấu hình trong `staticwebapp.config.json` và backend

## Cách Sử Dụng Static Web Apps CLI

```bash
# Login vào Azure
az login

# Liệt kê static web apps
az staticwebapp list

# Deploy
swa deploy ./out --env production --app-name YOUR_APP_NAME
``` 