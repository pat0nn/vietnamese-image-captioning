from flask import Blueprint, request, jsonify, send_from_directory, redirect, url_for, make_response, session
import bcrypt
import os
import uuid
import psycopg2
import psycopg2.extras
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from app.utils.db import get_db_connection
from app.utils.auth import generate_token, get_current_user, token_required, create_token
from app.config.settings import JWT_EXPIRATION_DELTA, UPLOAD_FOLDER, GCS_ENABLED
from app.utils.cloud_storage import upload_image, delete_image, get_image_url
from app.models.user import User
import io
from PIL import Image

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        # Check required fields
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({
                'success': False,
                'error': 'Username and password are required'
            }), 400
        
        username = data['username']
        password = data['password']
        admin_required = data.get('admin_only', False)  # Check if this is an admin-only login attempt
        
        print(f"Login attempt for user: {username}, Admin required: {admin_required}")
        
        # Get the user by username
        user = User.get_by_username(username)
        
        # User not found
        if not user:
            print(f"User not found: {username}")
            return jsonify({
                'success': False,
                'error': 'Invalid username or password'
            }), 401
        
        print(f"User found: {user['username']}, Password type: {type(user['password']).__name__}")
        print(f"User is_admin: {user['is_admin']}")
        
        # Check password
        if not User.verify_password(user['password'], password):
            print(f"Password verification failed for user: {username}")
            return jsonify({
                'success': False,
                'error': 'Invalid username or password'
            }), 401
        
        print(f"Password verified successfully for user: {username}")
        
        # If this is an admin dashboard login, verify admin rights
        if admin_required and not user['is_admin']:
            print(f"Admin access denied for user: {username}")
            return jsonify({
                'success': False,
                'error': 'Chỉ tài khoản admin mới có quyền truy cập trang quản trị'
            }), 403
        
        # Generate token
        print(f"Generating token for user ID: {user['id']}")
        token = create_token(
            user_id=str(user['id']),  # Ensure ID is a string for JWT
            username=user['username'],
            is_admin=user['is_admin']
        )
        
        print(f"Token generated successfully: {token[:15]}...")
        
        # Create a proper dict for JSON serialization
        user_dict = dict()
        
        # Copy key/value pairs, handling special cases
        for key in user.keys():
            # Skip password
            if key == 'password':
                continue
                
            # Handle datetime objects
            if key in ['created_at', 'updated_at'] and user[key] is not None:
                user_dict[key] = user[key].isoformat()
            else:
                user_dict[key] = user[key]
        
        print(f"User dict for response: {user_dict}")
        
        return jsonify({
            'success': True,
            'token': token,
            'user': user_dict
        })
        
    except Exception as e:
        print(f"Login error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    """User registration endpoint"""
    try:
        data = request.get_json()
        
        # Check required fields - email is now optional
        required_fields = ['username', 'password']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Set default email if not provided
        if 'email' not in data or not data['email']:
            data['email'] = f"{data['username']}@example.com"
        
        # Check if username or email already exists
        existing_user = User.get_by_username(data['username'])
        if existing_user:
            return jsonify({
                'success': False,
                'error': 'Username already exists'
            }), 409
        
        # Create the user
        new_user = User.create(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            full_name=data.get('full_name', ''),
            is_admin=False  # Regular users are not admins by default
        )
        
        if not new_user:
            return jsonify({
                'success': False,
                'error': 'Failed to create user'
            }), 500
        
        # Generate token
        token = create_token(
            user_id=new_user['id'],
            username=new_user['username'],
            is_admin=new_user['is_admin']
        )
        
        # Remove password from user data
        if 'password' in new_user:
            del new_user['password']
        
        # Format datetime objects for JSON
        if new_user['created_at']:
            new_user['created_at'] = new_user['created_at'].isoformat()
        if new_user['updated_at']:
            new_user['updated_at'] = new_user['updated_at'].isoformat()
        
        return jsonify({
            'success': True,
            'token': token,
            'user': new_user,
            'message': 'Registration successful'
        }), 201
        
    except Exception as e:
        print(f"Registration error: {e}")
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred'
        }), 500

@auth_bp.route('/logout', methods=['POST'])
@auth_bp.route('/api/logout', methods=['POST'])
def logout():
    print(f"Received logout request at {request.path}")
    
    # Create response
    response = jsonify({'message': 'Logout successful'})
    
    # Clear cookie
    response.delete_cookie('token', path='/')
    
    return response, 200

@auth_bp.route('/logout', methods=['GET'])
def logout_redirect():
    print(f"Redirecting from GET /logout to POST /api/logout")
    return logout()

@auth_bp.route('/user', methods=['GET'])
@auth_bp.route('/api/user', methods=['GET'])
def get_user():
    print(f"Received get user request at {request.path}")
    
    user_data = get_current_user(request)
    if not user_data:
        return jsonify({'error': 'Not authenticated', 'authenticated': False}), 401
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, username, is_admin FROM users WHERE id = %s", (user_data['id'],))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user:
            user_id, username, is_admin = user
            return jsonify({
                'authenticated': True,
                'user': {
                    'id': user_id,
                    'username': username,
                    'isAdmin': bool(is_admin)
                }
            })
        else:
            return jsonify({'error': 'User not found', 'authenticated': False}), 404
        
    except Exception as e:
        print(f"Error getting user: {str(e)}")
        return jsonify({'error': str(e), 'authenticated': False}), 500

@auth_bp.route('/api/profile', methods=['GET'])
@token_required
def get_profile(user_data):
    """Get detailed user profile information"""
    try:
        user_id = user_data['id']
        
        # Get full user profile data
        user = User.get_by_id(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'Không tìm thấy người dùng'
            }), 404
        
        # Format datetime objects for JSON
        user_dict = dict(user)
        if user_dict.get('created_at'):
            user_dict['created_at'] = user_dict['created_at'].isoformat()
        if user_dict.get('updated_at'):
            user_dict['updated_at'] = user_dict['updated_at'].isoformat()
        
        # Remove sensitive information
        if 'password' in user_dict:
            del user_dict['password']
        
        return jsonify({
            'success': True,
            'user': user_dict
        })
        
    except Exception as e:
        print(f"Error getting user profile: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_bp.route('/refresh-token', methods=['POST'])
@auth_bp.route('/api/refresh-token', methods=['POST'])
@token_required
def refresh_token(user_data):
    """
    Endpoint để làm mới token
    """
    try:
        user_id = user_data['id']
        username = user_data['username']
        
        # Tạo token mới
        new_token = generate_token(user_id, username)
        
        # Trả về token mới
        response = jsonify({
            'message': 'Token refreshed successfully',
            'token': new_token
        })
        
        # Cập nhật cookie
        max_age = 30 * 24 * 60 * 60  # 30 days in seconds
        expires = datetime.now() + timedelta(days=30)
        response.set_cookie(
            'token', 
            new_token, 
            max_age=max_age, 
            expires=expires, 
            httponly=False,
            secure=request.is_secure,
            samesite='Lax',
            path='/'
        )
        
        return response, 200
    except Exception as e:
        print(f"Error refreshing token: {str(e)}")
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/api/profile/update', methods=['PUT'])
@token_required
def update_profile(user_data):
    """Update user profile information"""
    try:
        data = request.get_json()
        user_id = user_data['id']
        
        # Fields that can be updated
        username = data.get('username')
        full_name = data.get('full_name')
        
        # Check if username already exists if it's being changed
        if username:
            existing_user = User.get_by_username(username)
            if existing_user and str(existing_user['id']) != str(user_id):
                return jsonify({
                    'success': False,
                    'error': 'Tên đăng nhập đã tồn tại'
                }), 400
        
        # Update user information
        updated = User.update(
            user_id=user_id,
            username=username,
            full_name=full_name
        )
        
        if not updated:
            return jsonify({
                'success': False,
                'error': 'Không thể cập nhật thông tin người dùng'
            }), 500
        
        # Get updated user data
        user = User.get_by_id(user_id)
        
        # Format datetime objects for JSON
        if user['created_at']:
            user['created_at'] = user['created_at'].isoformat()
        if user['updated_at']:
            user['updated_at'] = user['updated_at'].isoformat()
        
        # Create new token with updated username if it was changed
        token = None
        if username:
            token = create_token(
                user_id=str(user['id']),
                username=user['username'],
                is_admin=user['is_admin']
            )
        
        return jsonify({
            'success': True,
            'user': user,
            'token': token,  # Only include token if username was updated
            'message': 'Thông tin hồ sơ đã được cập nhật'
        })
        
    except Exception as e:
        print(f"Profile update error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_bp.route('/api/profile/update-password', methods=['PUT'])
@token_required
def update_password(user_data):
    """Update user password"""
    try:
        data = request.get_json()
        user_id = user_data['id']
        
        # Check required fields
        if not data or 'currentPassword' not in data or 'newPassword' not in data:
            return jsonify({
                'success': False,
                'error': 'Mật khẩu hiện tại và mật khẩu mới là bắt buộc'
            }), 400
        
        current_password = data['currentPassword']
        new_password = data['newPassword']
        
        # Get the user to verify current password
        user = User.get_by_id(user_id)
        if not user:
            return jsonify({
                'success': False,
                'error': 'Không tìm thấy người dùng'
            }), 404
        
        # Get full user data with password
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user_with_password = cursor.fetchone()
        cursor.close()
        conn.close()
        
        # Verify current password
        if not User.verify_password(user_with_password['password'], current_password):
            return jsonify({
                'success': False,
                'error': 'Mật khẩu hiện tại không đúng'
            }), 401
        
        # Update password
        updated = User.update_password(user_id, new_password)
        if not updated:
            return jsonify({
                'success': False,
                'error': 'Không thể cập nhật mật khẩu'
            }), 500
        
        return jsonify({
            'success': True,
            'message': 'Mật khẩu đã được cập nhật'
        })
        
    except Exception as e:
        print(f"Password update error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_bp.route('/api/profile/update-avatar', methods=['POST'])
@token_required
def update_avatar(user_data):
    """Update user avatar"""
    try:
        user_id = user_data['id']
        
        # Check if the post request has the file part
        if 'avatar' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Không tìm thấy file ảnh đại diện'
            }), 400
            
        file = request.files['avatar']
        
        # If user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Không có file nào được chọn'
            }), 400
            
        # Check if the file is an allowed image type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        if not '.' in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
            return jsonify({
                'success': False,
                'error': 'Định dạng file không được hỗ trợ'
            }), 400
            
        # Read file data
        file_data = file.read()
        image = Image.open(io.BytesIO(file_data)).convert('RGB')
        
        # Get current avatar to delete later
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Check if user has existing avatar
        cursor.execute(
            "SELECT avatar FROM users WHERE id = %s", 
            (user_id,)
        )
        user_record = cursor.fetchone()
        old_avatar = user_record['avatar'] if user_record else None
        
        # Generate unique filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        if GCS_ENABLED:
            # Upload ảnh lên Google Cloud Storage
            _, gcs_path, _ = upload_image(image, unique_filename, 'avatars')
            # Store only the filename, not the full path in the database
            if gcs_path and '/' in gcs_path:
                # In case GCS returns a path with directory structure
                gcs_path = gcs_path.split('/')[-1]
        else:
            # Lưu ảnh vào local storage
            avatar_folder = os.path.join(UPLOAD_FOLDER, 'avatars')
            os.makedirs(avatar_folder, exist_ok=True)
            file_path = os.path.join(avatar_folder, unique_filename)
            
            # Reset file pointer and save
            file.seek(0)
            file.save(file_path)
            
            # Store only the filename in the database, not the path
            gcs_path = unique_filename
        
        # Delete old avatar if exists
        if old_avatar and old_avatar != 'default.jpg':
            # Strip the directory path if present in old_avatar
            old_avatar_filename = old_avatar.split('/')[-1] if '/' in old_avatar else old_avatar
            
            if GCS_ENABLED:
                # Xóa từ Google Cloud Storage
                delete_image(old_avatar_filename)
            else:
                # Xóa từ local storage
                old_avatar_path = os.path.join(UPLOAD_FOLDER, 'avatars', old_avatar_filename)
                if os.path.exists(old_avatar_path):
                    os.remove(old_avatar_path)
        
        # Update user's avatar - only store the filename
        cursor.execute(
            """
            UPDATE users 
            SET avatar = %s, updated_at = NOW() 
            WHERE id = %s
            RETURNING id, username, avatar
            """, 
            (unique_filename, user_id)
        )
        updated_user = cursor.fetchone()
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Calculate the avatar URL
        if GCS_ENABLED:
            avatar_url = get_image_url(unique_filename)
        else:
            avatar_url = f"{request.url_root.rstrip('/')}/uploads/avatars/{unique_filename}"
        
        return jsonify({
            'success': True,
            'avatar_path': unique_filename,
            'avatar_url': avatar_url,
            'message': 'Ảnh đại diện đã được cập nhật'
        })
        
    except Exception as e:
        print(f"Avatar update error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
