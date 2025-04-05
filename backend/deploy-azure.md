# Triển khai Backend lên Azure Machine Learning

## Chuẩn bị Môi trường Azure

### 1. Cài đặt Azure CLI
```bash
# Kiểm tra Azure CLI
az --version

# Cài đặt extension Azure ML nếu chưa có
az extension add -n ml
```

### 2. Đăng nhập và tạo Resource Group
```bash
# Đăng nhập vào Azure
az login

# Tạo Resource Group
az group create --name image-caption-rg --location eastus
```

### 3. Tạo Azure ML Workspace
```bash
# Tạo workspace Azure ML
az ml workspace create --name image-caption-ws --resource-group image-caption-rg
```

## Chuẩn bị Database

### 1. Tạo PostgreSQL Database
```bash
# Tạo PostgreSQL server
az postgres server create \
    --resource-group image-caption-rg \
    --name image-caption-db \
    --location eastus \
    --admin-user adminuser \
    --admin-password '<your-password>' \
    --sku-name GP_Gen5_2

# Tạo firewall rule cho Azure services
az postgres server firewall-rule create \
    --resource-group image-caption-rg \
    --server-name image-caption-db \
    --name AllowAllAzureIPs \
    --start-ip-address 0.0.0.0 \
    --end-ip-address 0.0.0.0
```

### 2. Tạo Database và Tables
```bash
# Kết nối tới PostgreSQL server
psql -h image-caption-db.postgres.database.azure.com -U adminuser@image-caption-db -d postgres

# Tạo database
CREATE DATABASE image_caption_db;

# Kết nối tới database đã tạo
\c image_caption_db

# Tạo tables theo schema trong app.py
CREATE TABLE users (...);
CREATE TABLE images (...);
# Tạo thêm các bảng cần thiết
```

## Triển khai Model và API

### 1. Đăng ký model
```bash
# Đăng ký model
az ml model create \
    --name image-caption-model \
    --version 1 \
    --path . \
    --resource-group image-caption-rg \
    --workspace-name image-caption-ws
```

### 2. Tạo online endpoint
```bash
# Tạo online endpoint
az ml online-endpoint create \
    --name image-caption-endpoint \
    --resource-group image-caption-rg \
    --workspace-name image-caption-ws \
    --auth-mode key
```

### 3. Triển khai model lên endpoint
```bash
# Triển khai với biến môi trường
az ml online-deployment create \
    --name image-caption-deployment \
    --endpoint image-caption-endpoint \
    --file azure-ml-deployment.yml \
    --resource-group image-caption-rg \
    --workspace-name image-caption-ws \
    --set environment_variables.DB_HOST='image-caption-db.postgres.database.azure.com' \
    --set environment_variables.DB_NAME='image_caption_db' \
    --set environment_variables.DB_USER='adminuser@image-caption-db' \
    --set environment_variables.DB_PASSWORD='<your-password>' \
    --set environment_variables.SECRET_KEY='<your-secret-key>' \
    --set environment_variables.FRONTEND_URL='https://image-caption-webapp.azurestaticapps.net'
```

### 4. Kiểm tra endpoint
```bash
# Lấy URL của endpoint
az ml online-endpoint show \
    --name image-caption-endpoint \
    --resource-group image-caption-rg \
    --workspace-name image-caption-ws \
    --query scoring_uri -o tsv

# Test endpoint
curl -X GET https://image-caption-endpoint.eastus.inference.ml.azure.com/api/health
```

## Theo dõi và Debug

### 1. Xem logs của deployment
```bash
az ml online-deployment get-logs \
    --name image-caption-deployment \
    --endpoint image-caption-endpoint \
    --resource-group image-caption-rg \
    --workspace-name image-caption-ws
```

### 2. Cấu hình Application Insights
Trong Azure Portal, tạo và cấu hình Application Insights để theo dõi hiệu suất của ứng dụng. 