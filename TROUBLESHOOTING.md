# Hướng dẫn khắc phục sự cố

## Sự cố "Bạn chưa có đóng góp nào" khi đã có đóng góp trong database

Nếu bạn thấy thông báo "Bạn chưa có đóng góp nào" trên trang "Hồ sơ của tôi", nhưng chắc chắn rằng đã có đóng góp trong database, đây có thể là do một trong những vấn đề sau:

### 0. Sử dụng trang kiểm tra tự động

Chúng tôi đã tạo một công cụ kiểm tra tự động để giúp bạn xác định và giải quyết vấn đề:

1. **Truy cập trang kiểm tra**:
   - Mở trình duyệt và truy cập: `https://icy-river-037493600.6.azurestaticapps.net/test-ngrok`
   - Hoặc thêm `/test-ngrok` vào URL của ứng dụng

2. **Xác nhận URL ngrok**:
   - Nếu thấy lỗi kết nối ngrok, nhấn nút "Xác nhận URL Ngrok"
   - Nhấn "Visit Site" trong trang xác nhận ngrok
   - Quay lại trang kiểm tra và nhấn "Kiểm tra lại"

3. **Xem kết quả kiểm tra**:
   - Nếu tất cả các endpoint đều OK, vấn đề có thể nằm ở frontend
   - Nếu endpoint user/contributions trả về số lượng đóng góp > 0 nhưng trang hồ sơ không hiển thị, đó là lỗi hiển thị

### 1. Vấn đề trang xác nhận ngrok

Một trong những vấn đề phổ biến nhất là trang xác nhận bảo mật của ngrok. Khi sử dụng ngrok, lần đầu tiên truy cập URL, bạn phải chấp nhận điều khoản và xác nhận URL bằng tay:

1. **Xác nhận URL ngrok trước**:
   - Mỗi khi khởi động lại ngrok, bạn cần xác nhận URL mới
   - Mở trình duyệt và truy cập URL: `<ngrok-url>/api/ngrok-ready`
   - Nhấn nút "Visit Site" để xác nhận
   - Đợi cho đến khi thấy thông báo JSON `{"success": true, ...}`

2. **Xem log từ console**:
   - Nếu bạn thấy HTML được trả về thay vì JSON, đó là trang xác nhận ngrok
   - Chúng tôi đã thêm tham số `_ngrok_skip_browser_warning=true` vào tất cả các request
   - Nhưng vẫn cần xác nhận URL lần đầu trước khi tham số trên có tác dụng

### 2. Vấn đề API URL và CORS

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

### 3. Sửa đường dẫn ảnh

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

### 4. Kiểm tra thông qua API Test

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
     fetch('<ngrok-url>/api/test?_ngrok_skip_browser_warning=true').then(r => r.json()).then(console.log)
     ```

### 5. Kiểm tra database

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

### 6. Khởi động lại toàn bộ hệ thống

Nếu không giải quyết được, hãy thử:

1. Dừng và khởi động lại backend:
   ```bash
   cd vietnamese-image-captioning/backend
   ./run_with_ngrok.sh
   ```

2. Mở trình duyệt và xác nhận URL ngrok mới:
   - Truy cập: `<ngrok-url>/api/ngrok-ready`
   - Chấp nhận trang cảnh báo bằng cách nhấn "Visit Site"

3. Cập nhật URL mới trong Azure Portal

4. Chờ Azure build lại frontend (khoảng 1-2 phút)

5. Thử đăng nhập lại và kiểm tra trang "Hồ sơ của tôi"

## Liên hệ hỗ trợ

Nếu vẫn không giải quyết được vấn đề, hãy cung cấp các thông tin sau:

1. URL ngrok hiện tại
2. Ảnh chụp màn hình lỗi
3. Log từ Console trong Developer Tools (F12)
4. Nội dung JWT token (nhớ che đi một phần nếu chia sẻ công khai) 