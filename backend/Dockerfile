FROM python:3.11-slim

WORKDIR /app

# Cài đặt các gói phụ thuộc cần thiết cho các thư viện
RUN apt-get update && apt-get install -y \
    build-essential \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Sao chép requirements.txt trước để tận dụng cache của Docker
COPY requirements.txt .

# Cài đặt các gói Python
RUN pip install -r requirements.txt

# Sao chép tất cả các file còn lại
COPY . .

# Đảm bảo thư mục uploads tồn tại
RUN mkdir -p /app/uploads

# Thiết lập biến môi trường cho Google Cloud credentials
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/vietnamese-image-captioning-dd16a6c19d7f.json

# Thiết lập biến môi trường cho model
ENV MODEL_PATH=/app/artifacts

# Hiển thị nội dung thư mục artifacts để debug
RUN if [ -d "/app/artifacts" ]; then ls -la /app/artifacts; else echo "Artifacts directory not found"; fi

EXPOSE 5000 

CMD gunicorn -b 0.0.0.0:$PORT -w 4 --threads 2 --timeout 0 run:app


