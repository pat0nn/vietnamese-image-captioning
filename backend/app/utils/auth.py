import jwt
import bcrypt
from datetime import datetime
from flask import request, jsonify
from app.config.settings import SECRET_KEY, JWT_EXPIRATION_DELTA
from app.utils.db import get_db_connection
from functools import wraps
import os

# Use the SECRET_KEY from settings instead of a separate variable
# JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-for-development')

def generate_token(user_id, username):
    """
    Tạo JWT token cho người dùng đã xác thực
    """
    print(f"Generating token for user: {username} (ID: {user_id})")
    try:
        payload = {
            'exp': datetime.utcnow() + JWT_EXPIRATION_DELTA,
            'iat': datetime.utcnow(),
            'id': user_id,
            'username': username
        }
        # Đảm bảo token được trả về là chuỗi (string)
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        if isinstance(token, bytes):
            token = token.decode('utf-8')
            print("Converted token from bytes to string")
        
        print(f"Generated token (type: {type(token).__name__}): {token[:15]}...")
        return token
    except Exception as e:
        print(f"Error generating token: {str(e)}")
        raise

def decode_token(token):
    """
    Giải mã JWT token và trả về thông tin người dùng
    """
    try:
        print(f"Attempting to decode token (type: {type(token).__name__}): {token[:15]}...")
        
        # Đảm bảo token là chuỗi trước khi giải mã
        if isinstance(token, bytes):
            token = token.decode('utf-8')
            print("Converted token from bytes to string")
            
        # Giải mã token với xác thực chữ ký
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        print("Token decoded successfully with verification")
        return payload
    except jwt.ExpiredSignatureError:
        print("Token expired")
        return None
    except jwt.InvalidTokenError as e:
        print(f"Invalid token error: {str(e)}")
        return None
    except Exception as e:
        print(f"Unexpected token decoding error: {str(e)}")
        return None

def get_current_user(request):
    """
    Lấy thông tin người dùng hiện tại từ request
    """
    # Try to get token from Authorization header first
    auth_header = request.headers.get('Authorization')
    print(f"Auth header: {auth_header if auth_header else 'None'}")
    
    token = None
    
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(" ")[1]
        print(f"Token extracted from Auth header: {token[:10]}...")
    else:
        # Then try to get from cookies
        token = request.cookies.get('token')
        print(f"Cookie token: {token[:10] if token else 'None'}...")
    
    if not token:
        print("No token found in request")
        return None
    
    # Decode and verify the token
    try:
        print(f"Decoding token: {token[:10]}...")
        user_data = decode_token(token)
        if user_data:
            print(f"Token valid for user: {user_data.get('username')}")
            return user_data
        else:
            print("Token decode returned None (invalid token)")
            return None
    except Exception as e:
        print(f"Token verification error: {str(e)}")
        return None

def is_admin(user_id):
    """
    Kiểm tra xem người dùng có quyền admin không
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT is_admin FROM users WHERE id = %s", (user_id,))
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return result and result[0]
    except Exception as e:
        print(f"Error checking admin status: {str(e)}")
        return False

def token_required(f):
    """
    Decorator để bảo vệ route với token authentication
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_data = get_current_user(request)
        
        if not user_data:
            return jsonify({'error': 'Unauthorized', 'authenticated': False}), 401
        
        # If 'id' is missing but 'sub' exists, copy 'sub' to 'id'
        if 'id' not in user_data and 'sub' in user_data:
            user_data['id'] = user_data['sub']
            print(f"Converted legacy token format: copied 'sub' key ({user_data['sub']}) to 'id' key")
            
        # Thêm thông tin user vào kwargs để function có thể sử dụng
        kwargs['user_data'] = user_data
        
        return f(*args, **kwargs)
    
    return decorated_function

def create_token(user_id, username, is_admin):
    """Create a JWT token for the user"""
    payload = {
        'id': user_id,
        'username': username,
        'is_admin': is_admin,
        'created_at': datetime.utcnow().isoformat()
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def verify_token(token):
    """Verify the JWT token and return the payload"""
    try:
        # Decode and verify the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return {'success': True, 'payload': payload}
    except jwt.ExpiredSignatureError:
        return {'success': False, 'error': 'Token expired'}
    except jwt.InvalidTokenError:
        return {'success': False, 'error': 'Invalid token'}

def auth_required(f):
    """Decorator to check if user is authenticated"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Get the token from the header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        
        # Extract the token
        token = auth_header.split(' ')[1]
        if not token:
            return jsonify({'success': False, 'error': 'Token is missing'}), 401
        
        # Verify the token
        result = verify_token(token)
        if not result['success']:
            return jsonify({'success': False, 'error': result['error']}), 401
        
        # Add user data to kwargs
        kwargs['user_data'] = result['payload']
        
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    """Decorator to check if user is an admin"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # First check if user is authenticated
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        
        # Extract the token
        token = auth_header.split(' ')[1]
        if not token:
            return jsonify({'success': False, 'error': 'Token is missing'}), 401
        
        # Verify the token
        result = verify_token(token)
        if not result['success']:
            return jsonify({'success': False, 'error': result['error']}), 401
        
        # Check if user is admin
        if not result['payload'].get('is_admin', False):
            return jsonify({'success': False, 'error': 'Admin privileges required'}), 403
        
        # Add user data to kwargs
        kwargs['user_data'] = result['payload']
        
        return f(*args, **kwargs)
    return decorated
