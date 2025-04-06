# Hướng dẫn khắc phục sự cố

## Sự cố "Bạn chưa có đóng góp nào" khi đã có đóng góp trong database

Nếu bạn thấy thông báo "Bạn chưa có đóng góp nào" trên trang "Hồ sơ của tôi", nhưng chắc chắn rằng đã có đóng góp trong database, đây có thể là do một trong những vấn đề sau:

### 1. Vấn đề API URL và CORS

Khi frontend được deploy trên Azure Static Web Apps và backend chạy qua ngrok, chúng ta cần đảm bảo:

1. **Kiểm tra biến môi trường `NEXT_PUBLIC_API_URL`**:
   - Trong Azure Portal, đi đến trang Static Web App của bạn
   - Vào mục Configuration > Application Settings
   - Kiểm tra xem biến `NEXT_PUBLIC_API_URL` đã được cấu hình đúng với URL ngrok hiện tại (bao gồm `/api` ở cuối)
   
2. **Kiểm tra URL ngrok**:
   - Sau mỗi lần khởi động lại ngrok, URL sẽ thay đổi
   - Chạy `./run_with_ngrok.sh` và ghi nhớ URL mới
   - Cập nhật biến môi trường trong Azure Portal

3. **Kiểm tra JWT token**:
   - Mở trình duyệt, nhấn F12 để mở Developer Tools
   - Vào tab Console và gõ:
     ```javascript
     localStorage.getItem('auth_token')
     ```
   - Nếu không có token hoặc token là null, hãy đăng nhập lại

### 2. Sửa đường dẫn ảnh

Một vấn đề phổ biến là đường dẫn ảnh không đúng. Trong file `UserContributions.js`, chúng ta đã sửa đường dẫn ảnh để sử dụng URL động:

```javascript
<Image 
  src={`${BASE_URL}/uploads/${item.image_path}`}
  alt={item.user_caption || 'Hình ảnh đóng góp'}
  width={200}
  height={200}
  style={{ objectFit: 'cover', cursor: 'pointer' }}
/>
```

Nếu vẫn gặp vấn đề, kiểm tra Console trong Developer Tools để xem:

```
Image path: <đường dẫn ảnh>
Base URL: <URL cơ sở>
```

### 3. Kiểm tra thông qua API Test

Để kiểm tra API trực tiếp:

1. **Kiểm tra token JWT**:
   - Truy cập URL: `<ngrok-url>/api/test-auth` trong trình duyệt
   - Mở Developer Tools (F12), vào tab Network
   - Nhấn F5 để refresh và xem response

2. **Kiểm tra CORS**:
   - Truy cập URL: `<ngrok-url>/api/test` trong trình duyệt
   - Đảm bảo bạn thấy thông báo "CORS test successful"

3. **Kiểm tra kết nối đến backend**:
   - Trong Console của Developer Tools, chạy:
     ```javascript
     fetch('<ngrok-url>/api/test').then(r => r.json()).then(console.log)
     ```

### 4. Kiểm tra database

Nếu các bước trên không giải quyết được vấn đề, kết nối trực tiếp đến PostgreSQL database để kiểm tra:

```bash
psql -h localhost -U postgres -d image_caption_db
```

Sau đó chạy truy vấn:

```sql
SELECT * FROM users WHERE username = 'your_username';
-- Lấy user_id từ kết quả trên
SELECT * FROM images WHERE user_id = user_id_from_above;
```

### 5. Khởi động lại toàn bộ hệ thống

Nếu không giải quyết được, hãy thử:

1. Dừng và khởi động lại backend:
   ```bash
   cd vietnamese-image-captioning/backend
   ./run_with_ngrok.sh
   ```

2. Cập nhật URL mới trong Azure Portal

3. Chờ Azure build lại frontend (khoảng 1-2 phút)

4. Thử đăng nhập lại và kiểm tra trang "Hồ sơ của tôi"

## Liên hệ hỗ trợ

Nếu vẫn không giải quyết được vấn đề, hãy cung cấp các thông tin sau:

1. URL ngrok hiện tại
2. Ảnh chụp màn hình lỗi
3. Log từ Console trong Developer Tools (F12)
4. Nội dung JWT token (nhớ che đi một phần nếu chia sẻ công khai) 