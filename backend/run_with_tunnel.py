import os
import sys
import subprocess
import time
from pyngrok import ngrok, conf
import requests
import json
import signal

# Cấu hình ngrok
NGROK_AUTH_TOKEN = "2ulV9YargynIssbaHdbS3LEzj1o_7sL4vXh3rLFaZoAUkQehv"  # Điền token của bạn nếu bạn đã đăng ký tài khoản ngrok
BACKEND_PORT = 5000

# Đảm bảo server Flask có thể nhận biết rằng nó đang chạy sau proxy
os.environ["FLASK_RUN_BEHIND_PROXY"] = "true"

def save_frontend_env(public_url):
    """Lưu URL công khai vào file .env.local cho frontend"""
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                           "frontend", ".env.local")
    
    with open(env_path, "w") as f:
        f.write(f"NEXT_PUBLIC_API_URL={public_url}/api\n")
        f.write(f"NEXT_PUBLIC_BACKEND_HOST={public_url.replace('https://', '').replace('http://', '')}\n")
        f.write(f"NEXT_PUBLIC_BACKEND_PORT=\n")
    
    print(f"Đã cập nhật file .env.local với URL: {public_url}")

def signal_handler(sig, frame):
    print("\nĐang dừng ngrok tunnel...")
    ngrok.kill()
    print("Đã đóng ngrok tunnel. Kết thúc chương trình.")
    sys.exit(0)

def run_flask_with_tunnel():
    # Đăng ký signal handler để xử lý đóng tunnel khi tắt ứng dụng
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Cấu hình ngrok để tăng độ ổn định
        conf.get_default().region = 'us'  # Chọn region gần nhất
        conf.get_default().console_ui = False
        
        # Thiết lập ngrok nếu có auth token
        if NGROK_AUTH_TOKEN:
            ngrok.set_auth_token(NGROK_AUTH_TOKEN)
            print(f"Đã thiết lập ngrok auth token")
        
        # Mở tunnel đến cổng của Flask
        tunnel = ngrok.connect(BACKEND_PORT, bind_tls=True)
        public_url = tunnel.public_url
        
        # Đảm bảo URL bắt đầu bằng https
        if not public_url.startswith("https"):
            public_url = public_url.replace("http", "https")
        
        print(f"\n======= THÔNG TIN NGROK TUNNEL =======")
        print(f"Ngrok tunnel đang chạy tại: {public_url}")
        print(f"Backend API có thể truy cập tại: {public_url}/api")
        print(f"Uploads có thể truy cập tại: {public_url}/uploads")
        print(f"=====================================\n")
        
        # Lưu URL vào file .env.local cho frontend
        save_frontend_env(public_url)
        
        # In hướng dẫn cập nhật Azure Static Web App
        print("\n===== HƯỚNG DẪN DEPLOY FRONTEND =====")
        print("1. Cập nhật biến môi trường trong Azure Static Web App:")
        print(f"   NEXT_PUBLIC_API_URL={public_url}/api")
        print(f"   NEXT_PUBLIC_BACKEND_HOST={public_url.replace('https://', '').replace('http://', '')}")
        print("   NEXT_PUBLIC_BACKEND_PORT=")
        print("2. Rebuild và redeploy frontend lên Azure Static Web App")
        print("======================================\n")
        
        # Chạy Flask app
        print("Đang khởi động Flask backend...")
        try:
            # Sử dụng sys.executable để đảm bảo chạy cùng môi trường Python
            subprocess.run([sys.executable, "app.py"])
        except KeyboardInterrupt:
            print("Đang dừng ngrok tunnel...")
            ngrok.kill()
            print("Đã đóng ngrok tunnel. Kết thúc chương trình.")
    except Exception as e:
        print(f"Lỗi khởi động ngrok tunnel: {str(e)}")
        # Đảm bảo ngrok được đóng cả khi có lỗi
        try:
            ngrok.kill()
        except:
            pass
        sys.exit(1)

if __name__ == "__main__":
    run_flask_with_tunnel() 