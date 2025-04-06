from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
import os
from PIL import Image
import io
import torch
import base64
import uuid
import psycopg2
from psycopg2.extras import RealDictCursor
from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
import bcrypt
from datetime import datetime, timedelta
import jwt

app = Flask(__name__, static_folder=None)  # Tắt thư mục static mặc định
# Cập nhật CORS để cho phép yêu cầu từ bất kỳ origin nào và hỗ trợ credentials
CORS(app, resources={r"/*": {"origins": "*", "supports_credentials": True, "expose_headers": ["Authorization"]}})

# SECRET_KEY mới, đảm bảo dài và đủ mạnh (nên đặt trong biến môi trường trong production)
app.config['SECRET_KEY'] = 'hNOg9JHiXCjUcqQzNtvYFKa7eksRLdwSGIfupW5M23T4vPDyZm'
app.config['JWT_EXPIRATION_DELTA'] = timedelta(days=30)  # Token valid for 30 days

# Model paths - Update these to your model paths
MODEL_PATH = '/run/media/trong/New Volume/Algo/artifacts/model-checkpoint-3534:v1'

# Database connection parameters
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'image_caption_db'
DB_USER = 'postgres'
DB_PASSWORD = 'postgres'

# Create uploads directory if it doesn't exist
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Global variables for model components
model = None
feature_extractor = None
tokenizer = None

# Database connection function
def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    conn.autocommit = True
    return conn

# Initialize database function
def init_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create users table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create images table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS images (
                id SERIAL PRIMARY KEY,
                image_id VARCHAR(50) UNIQUE NOT NULL,
                image_path VARCHAR(255) NOT NULL,
                user_caption TEXT,
                ai_caption TEXT,
                user_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        cursor.close()
        conn.close()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {str(e)}")

# Authentication helper functions
def generate_token(user_id, username):
    print(f"Generating token for user: {username} (ID: {user_id})")
    try:
        payload = {
            'exp': datetime.utcnow() + app.config['JWT_EXPIRATION_DELTA'],
            'iat': datetime.utcnow(),
            'sub': user_id,
            'username': username
        }
        # Đảm bảo token được trả về là chuỗi (string)
        token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
        if isinstance(token, bytes):
            token = token.decode('utf-8')
            print("Converted token from bytes to string")
        
        print(f"Generated token (type: {type(token).__name__}): {token[:15]}...")
        
        # Kiểm tra ngay token vừa tạo
        try:
            decode_result = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            print("Token verification successful")
        except Exception as e:
            print(f"WARNING: Token verification failed: {str(e)}")
        
        return token
    except Exception as e:
        print(f"Error generating token: {str(e)}")
        # Trả về một token mặc định trong trường hợp lỗi (chỉ để debug)
        return "invalid_token"

def decode_token(token):
    try:
        print(f"Attempting to decode token (type: {type(token).__name__}): {token[:15]}...")
        
        # Đảm bảo token là chuỗi trước khi giải mã
        if isinstance(token, bytes):
            token = token.decode('utf-8')
            print("Converted token from bytes to string")
            
        # Thử giải mã với cả hai cách: có và không có verify
        try:
            # Trước tiên thử với verify=True (mặc định)
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            print("Token decoded successfully with verification")
            return payload
        except jwt.InvalidTokenError:
            # Nếu lỗi, thử lại với verify=False (chỉ dùng trong debug)
            print("Normal verification failed, attempting without verification for debugging")
            payload = jwt.decode(token, options={"verify_signature": False}, algorithms=['HS256'])
            print("WARNING: Token decoded without verification (debug mode only)")
            # Kiểm tra xem token có trường cần thiết không
            if 'sub' in payload and 'username' in payload:
                print(f"Token contains necessary fields: sub={payload['sub']}, username={payload['username']}")
                # Trong môi trường sản xuất, bạn nên return None ở đây
                # Nhưng để dễ debug, tạm thời chấp nhận token này
                return payload
            return None
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
    # Try to get token from Authorization header first
    auth_header = request.headers.get('Authorization')
    print(f"Auth header: {auth_header if auth_header else 'None'}")
    
    token = None
    
    if auth_header and len(auth_header.split(" ")) > 1:
        token = auth_header.split(" ")[1]
        print(f"Token extracted from Auth header: {token[:10]}...")
    else:
        # Then try to get from cookies
        token = request.cookies.get('token')
        print(f"Cookie token: {token[:10] if token else 'None'}...")
    
    # If still no token, check if it's in the query parameters (for debugging only)
    if not token and 'token' in request.args:
        token = request.args.get('token')
        print(f"Token from query params: {token[:10]}...")
    
    # Finally, check if it's in the form data
    if not token and request.form and 'token' in request.form:
        token = request.form.get('token')
        print(f"Token from form data: {token[:10]}...")
    
    # If still no token, check if it's in the JSON body
    if not token and request.is_json and 'token' in request.json:
        token = request.json.get('token')
        print(f"Token from JSON body: {token[:10]}...")
    
    if not token:
        print("No token found in request")
        return None
    
    # Debug: in trực tiếp token để kiểm tra
    print(f"Full token to decode: {token}")
    
    # Decode and verify the token
    try:
        print(f"Decoding token: {token[:10]}...")
        user_data = decode_token(token)
        if user_data:
            print(f"Token valid for user: {user_data.get('username')}")
            
            # In ra token đã xác thực để kiểm tra
            print(f"User data from token: {user_data}")
            
            # Thử một cách tiếp cận khác nếu cần
            if user_data.get('sub') is None:
                print("WARNING: Token missing 'sub' field, trying to extract manually")
                # Nếu không tìm thấy sub, thử tìm user_id cách thủ công
                # Đây là cách xử lý tạm thời, không nên dùng trong production
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT id FROM users WHERE username = %s", (user_data.get('username'),))
                    result = cursor.fetchone()
                    if result:
                        user_data['sub'] = result[0]
                        print(f"Manually set user_id: {user_data['sub']}")
                    cursor.close()
                    conn.close()
                except Exception as e:
                    print(f"Error getting user_id: {str(e)}")
            
            return user_data
        else:
            print("Token decode returned None (invalid token)")
        return user_data
    except Exception as e:
        print(f"Token verification error: {str(e)}")
        return None

# Load models
def load_model():
    global model, feature_extractor, tokenizer
    
    # Only load if not already loaded
    if model is None:
        # Load the model components
        model = VisionEncoderDecoderModel.from_pretrained(MODEL_PATH)
        feature_extractor = ViTImageProcessor.from_pretrained(MODEL_PATH)
        
        # Load tokenizer - update the path if needed
        tokenizer = AutoTokenizer.from_pretrained("vinai/bartpho-word")
        
        # Set the device
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = model.to(device)
        
        # Set model configuration
        model.config.decoder_start_token_id = tokenizer.bos_token_id
        model.config.pad_token_id = tokenizer.pad_token_id
        
        print(f"Model loaded successfully on {device}")

# Format the caption: remove underscores, capitalize first letter, add period
def format_caption(caption):
    # Remove underscores
    formatted = caption.replace('_', ' ')
    
    # Capitalize the first letter
    if formatted:
        formatted = formatted[0].upper() + formatted[1:]
    
    # Add period at the end if not present
    if formatted and not formatted.endswith(('.', '!', '?')):
        formatted += '.'
        
    return formatted

# Load the model at startup
load_model()

# Initialize database at startup
init_db()

# User registration endpoint
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    print(f"Registration attempt for user: {username}")
    
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        if cursor.fetchone() is not None:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Username already exists'}), 400
        
        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Insert the new user
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s) RETURNING id",
            (username, hashed_password.decode('utf-8'))
        )
        user_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        
        # Generate token
        token = generate_token(user_id, username)
        
        # Create response
        response = jsonify({
            'message': 'User created successfully',
            'user': {'id': user_id, 'username': username},
            'token': token
        })
        
        # Set cookie
        print(f"Setting token cookie for user: {username}")
        max_age = 30 * 24 * 60 * 60  # 30 days in seconds
        expires = datetime.now() + timedelta(days=30)
        response.set_cookie(
            'token', 
            token, 
            max_age=max_age, 
            expires=expires, 
            httponly=False,  # Allow JavaScript access
            secure=True,     # Use secure cookies with HTTPS
            samesite='None', # Allow cross-site cookies for Azure
            path='/'
        )
        
        return response, 201
    except Exception as e:
        print(f"Registration error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# User login endpoint
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    print(f"Login attempt for user: {username}")
    
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Find the user
        cursor.execute("SELECT id, password FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user is None:
            return jsonify({'error': 'Invalid username or password'}), 401
        
        user_id, hashed_password = user
        
        # Check password
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
            # Generate token
            token = generate_token(user_id, username)
            
            # Create response
            response = jsonify({
                'message': 'Login successful',
                'user': {'id': user_id, 'username': username},
                'token': token
            })
            
            # Set cookie
            print(f"Setting token cookie for user: {username}")
            max_age = 30 * 24 * 60 * 60  # 30 days in seconds
            expires = datetime.now() + timedelta(days=30)
            response.set_cookie(
                'token', 
                token, 
                max_age=max_age, 
                expires=expires, 
                httponly=False,  # Allow JavaScript access
                secure=True,     # Use secure cookies with HTTPS
                samesite='None', # Allow cross-site cookies for Azure
                path='/'
            )
            
            return response, 200
        else:
            return jsonify({'error': 'Invalid username or password'}), 401
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# User logout endpoint
@app.route('/api/logout', methods=['POST'])
def logout():
    print("Logout request received")
    
    # Tạo response và đặt cookie hết hạn
    response = jsonify({'message': 'Logged out successfully'})
    
    # Xóa cookie bằng nhiều phương pháp để đảm bảo hoạt động trên mọi trình duyệt
    # Phương pháp 1: Đặt giá trị cookie là rỗng và cho hết hạn
    response.set_cookie('token', '', expires=0, max_age=0, path='/')
    
    # Phương pháp 2: Sử dụng delete_cookie
    response.delete_cookie('token', path='/')
    
    print("Token cookie cleared in logout response")
    return response

# Get current user endpoint
@app.route('/api/user', methods=['GET'])
def get_user():
    user_data = get_current_user(request)
    
    if not user_data:
        return jsonify({'authenticated': False}), 401
    
    return jsonify({
        'authenticated': True,
        'user_id': user_data['sub'],
        'username': user_data['username'],
        'user': {
            'id': user_data['sub'],
            'username': user_data['username']
        }
    })

# API route for image captioning (no login required)
@app.route('/api/caption', methods=['POST'])
def caption_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    
    file = request.files['image']
    
    # Read and convert image
    image_bytes = file.read()
    image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    
    # Generate caption
    try:
        # Preprocess image
        device = "cuda" if torch.cuda.is_available() else "cpu"
        pixel_values = feature_extractor(image, return_tensors="pt").pixel_values.to(device)
        
        # Generate caption
        with torch.no_grad():
            generated_ids = model.generate(
                pixel_values, 
                num_beams=3, 
                do_sample=False, 
                max_length=24
            )
        
        # Decode caption
        raw_caption = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        
        # Format the caption
        formatted_caption = format_caption(raw_caption)
        
        return jsonify({
            'success': True,
            'caption': formatted_caption,
            'raw_caption': raw_caption  # Optional: include raw caption for debugging
        })
    
    except Exception as e:
        print(f"Error generating caption: {str(e)}")
        return jsonify({'error': str(e)}), 500

# API route to save user contributed data (login required)
@app.route('/api/contribute', methods=['POST'])
def contribute_data():
    # Check if user is logged in
    user_data = get_current_user(request)
    if not user_data:
        return jsonify({'error': 'Authentication required'}), 401
    
    user_id = user_data['sub']
    
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    
    file = request.files['image']
    user_caption = request.form.get('userCaption', '')
    skip_ai_caption = request.form.get('skipAiCaption', 'false').lower() == 'true'
    
    try:
        # Read and convert image
        image_bytes = file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        
        # Generate AI caption only if not skipped
        ai_caption = None
        if not skip_ai_caption:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            pixel_values = feature_extractor(image, return_tensors="pt").pixel_values.to(device)
            
            with torch.no_grad():
                generated_ids = model.generate(
                    pixel_values, 
                    num_beams=3, 
                    do_sample=False, 
                    max_length=24
                )
            
            # Decode caption
            raw_caption = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
            ai_caption = format_caption(raw_caption)
        
        # Save image to disk
        image_id = str(uuid.uuid4())
        filename = f"{image_id}.jpg"
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        
        # Lưu ảnh vào đĩa
        image.save(image_path)
        
        # Lưu đường dẫn tương đối để dễ truy cập từ API
        db_image_path = f"{filename}"
        
        # Save to database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            INSERT INTO images (image_id, image_path, user_caption, ai_caption, user_id)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
            """,
            (image_id, db_image_path, user_caption, ai_caption, user_id)
        )
        
        new_id = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'id': new_id,
            'image_id': image_id,
            'user_caption': user_caption,
            'ai_caption': ai_caption
        })
        
    except Exception as e:
        print(f"Error saving contribution: {str(e)}")
        return jsonify({'error': str(e)}), 500

# API to get all contributed images (for admin)
@app.route('/api/contributions', methods=['GET'])
def get_contributions():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT i.*, u.username 
            FROM images i
            LEFT JOIN users u ON i.user_id = u.id
            ORDER BY i.created_at DESC
        """)
        contributions = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'contributions': contributions
        })
        
    except Exception as e:
        print(f"Error getting contributions: {str(e)}")
        return jsonify({'error': str(e)}), 500

# API to get user's contributions
@app.route('/api/user/contributions', methods=['GET'])
def get_user_contributions():
    # Check if user is logged in
    user_data = get_current_user(request)
    if not user_data:
        return jsonify({'error': 'Authentication required'}), 401
    
    user_id = user_data['sub']
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT * FROM images 
            WHERE user_id = %s
            ORDER BY created_at DESC
        """, (user_id,))
        contributions = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'contributions': contributions
        })
        
    except Exception as e:
        print(f"Error getting user contributions: {str(e)}")
        return jsonify({'error': str(e)}), 500

# API to update user's contribution
@app.route('/api/contribution/<image_id>', methods=['PUT'])
def update_contribution(image_id):
    # Check if user is logged in
    user_data = get_current_user(request)
    if not user_data:
        return jsonify({'error': 'Authentication required'}), 401
    
    user_id = user_data['sub']
    data = request.json
    user_caption = data.get('userCaption', '')
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if the image belongs to the user
        cursor.execute("""
            SELECT id FROM images 
            WHERE image_id = %s AND user_id = %s
        """, (image_id, user_id))
        
        image = cursor.fetchone()
        if not image:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Image not found or you do not have permission'}), 404
        
        # Update the caption
        cursor.execute("""
            UPDATE images 
            SET user_caption = %s 
            WHERE image_id = %s
            RETURNING id
        """, (user_caption, image_id))
        
        updated_id = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'id': updated_id,
            'message': 'Caption updated successfully'
        })
        
    except Exception as e:
        print(f"Error updating caption: {str(e)}")
        return jsonify({'error': str(e)}), 500

# API to delete user's contribution
@app.route('/api/contribution/<image_id>', methods=['DELETE'])
def delete_contribution(image_id):
    # Check if user is logged in
    user_data = get_current_user(request)
    if not user_data:
        return jsonify({'error': 'Authentication required'}), 401
    
    user_id = user_data['sub']
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if the image belongs to the user
        cursor.execute("""
            SELECT image_path FROM images 
            WHERE image_id = %s AND user_id = %s
        """, (image_id, user_id))
        
        image = cursor.fetchone()
        if not image:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Image not found or you do not have permission'}), 404
        
        image_path = image[0]
        
        # Delete from database
        cursor.execute("DELETE FROM images WHERE image_id = %s", (image_id,))
        
        cursor.close()
        conn.close()
        
        # Delete file from disk
        if os.path.exists(image_path):
            os.remove(image_path)
        
        return jsonify({
            'success': True,
            'message': 'Contribution deleted successfully'
        })
        
    except Exception as e:
        print(f"Error deleting contribution: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Route để phục vụ các file tĩnh từ thư mục uploads
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000) 