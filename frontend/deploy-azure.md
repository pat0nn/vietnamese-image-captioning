# Triển khai Frontend lên Azure Static Web Apps

## Chuẩn bị

### 1. Tạo tài nguyên Azure Static Web App

```bash
# Tạo Static Web App resource
az staticwebapp create \
  --name image-caption-webapp \
  --resource-group image-caption-rg \
  --location "East US 2" \
  --source https://github.com/yourusername/image-uploader \
  --branch main \
  --app-location "/frontend" \
  --output-location "out" \
  --login-with-github
```

### 2. Thiết lập GitHub Repository

1. Push code lên GitHub repository
2. Kết nối repository với Azure Static Web Apps thông qua Azure Portal
3. Azure sẽ tự động thêm GitHub Action workflow vào repository

### 3. Thiết lập Environment Variables

Trong Azure Portal, thiết lập biến môi trường sau:

- `NEXT_PUBLIC_API_URL`: URL của backend API (lấy từ Azure ML endpoint)
  - Ví dụ: `https://image-caption-endpoint.eastus.azureml.ms/api`

## Triển khai thủ công

Nếu bạn muốn triển khai thủ công thay vì sử dụng GitHub Actions:

```bash
# Build và export
cd image-uploader/frontend
npm install
NEXT_PUBLIC_API_URL=https://your-backend-url.azureml.ms/api npm run build && npm run export

# Triển khai lên Azure Static Web Apps
az staticwebapp deploy \
  --name image-caption-webapp \
  --resource-group image-caption-rg \
  --source "out" \
  --no-wait
```

## Cấu hình Routes

Đã thiết lập trong file `staticwebapp.config.json` để:
- Điều hướng client-side đúng cách
- Bảo vệ route `/profile` cho người dùng đã đăng nhập
- Điều hướng người dùng chưa đăng nhập về trang chủ

## Kiểm tra Triển khai

Sau khi triển khai, kiểm tra các tính năng sau:
1. Đăng ký và đăng nhập hoạt động
2. Tải ảnh và nhận caption hoạt động
3. Quản lý đóng góp hoạt động
4. Bảo mật route `/profile` hoạt động

## Sửa lỗi Phổ biến

1. Lỗi CORS: Cập nhật cấu hình CORS trong backend để cho phép origin của Static Web App
2. Lỗi authen: Đảm bảo cookie được thiết lập đúng domain và secure flags
3. Lỗi hình ảnh: Đảm bảo endpoint API uploads hoạt động đúng 