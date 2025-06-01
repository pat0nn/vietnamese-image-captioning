from flask import request, jsonify
from app.config.settings import ALLOWED_ORIGINS

def add_cors_headers(response):
    """
    Thêm CORS headers cho mọi response
    """
    origin = request.headers.get('Origin')
    
    # Nếu có Origin header
    if origin:
        # Kiểm tra xem origin có thuộc danh sách được phép không
        if origin in ALLOWED_ORIGINS or origin.endswith('.phambatrong.com') or origin.startswith('http://localhost') or origin.startswith('https://vietnamese-image-captioning.web.app') or origin.startswith('https://vietnamese-image-captioning.firebaseapp.com'):
            # Cho phép origin cụ thể và credentials
            response.headers.add('Access-Control-Allow-Origin', origin)
            response.headers.add('Access-Control-Allow-Credentials', 'true')
        else:
            # Nếu origin không nằm trong danh sách, cho phép tất cả nhưng không hỗ trợ credentials
            response.headers.add('Access-Control-Allow-Origin', '*')
            # Không thêm Allow-Credentials khi dùng Allow-Origin: *
        
        # Các header khác áp dụng cho tất cả request
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        # Thêm header để cho phép cache preflight request để cải thiện hiệu suất
        response.headers.add('Access-Control-Max-Age', '86400')  # 24 giờ
    
    # In ra thông tin headers để debug
    print(f"Request Origin: {origin}")
    print(f"Response CORS headers: {dict(response.headers)}")
    
    return response

def handle_options_request(path=None):
    """
    Xử lý riêng cho OPTIONS request
    """
    print(f"OPTIONS request headers: {request.headers}")
    print(f"Request Origin: {request.headers.get('Origin')}")
    
    # Simply return OK status - Flask-CORS will add the headers
    return jsonify({'status': 'ok'}), 200
