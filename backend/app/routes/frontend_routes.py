from flask import Blueprint, jsonify, send_from_directory, current_app, request
import os
from app.config.settings import FRONTEND_STATIC_FOLDER
from app.utils.auth import get_current_user
from app.utils.db import get_db_connection
import json
from datetime import date

frontend_bp = Blueprint('frontend', __name__)

def track_visit():
    """Track a user visit"""
    try:
        # Get user info if available
        user_data = get_current_user(request)
        user_id = user_data['id'] if user_data else None
        
        # Get IP address
        ip_address = request.remote_addr
        
        # Get user agent
        user_agent = request.headers.get('User-Agent', '')
        
        # Additional details
        details = {
            'path': request.path,
            'user_agent': user_agent,
            'referrer': request.referrer
        }
        
        # Insert into database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO user_activities (activity_type, user_id, ip_address, details)
                VALUES (%s, %s, %s, %s)
            """, ('visit', user_id, ip_address, json.dumps(details)))
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Error inserting visit data: {e}")
        finally:
            cursor.close()
            conn.close()
        
    except Exception as e:
        print(f"Error tracking visit: {e}")

# Route để phục vụ ứng dụng React từ thư mục static
@frontend_bp.route('/', defaults={'path': ''})
@frontend_bp.route('/<path:path>')
def serve_frontend(path):
    # Track visit for page loads (not for asset requests)
    if not path or not ('.' in path and path.rsplit('.', 1)[1] in ['js', 'css', 'png', 'jpg', 'jpeg', 'gif', 'svg', 'ico', 'woff', 'woff2', 'ttf']):
        track_visit()
    
    print(f"Serving request for path: /{path}")
    
    # Kiểm tra nếu path bắt đầu bằng api, uploads hoặc là một OPTIONS request
    if path.startswith('api/') or path.startswith('uploads/'):
        print(f"Forwarding to API route: /{path}")
        # Chuyển qua các route API khác
        return frontend_bp.make_response(('', 404))
    
    # Make sure the FRONTEND_STATIC_FOLDER exists
    if not os.path.exists(FRONTEND_STATIC_FOLDER):
        print(f"ERROR: Static folder does not exist: {FRONTEND_STATIC_FOLDER}")
        return jsonify({"error": "Static folder not found"}), 500
    
    # Direct file match for static resources (like _next/static/*)
    if path.startswith('_next/'):
        static_file_path = os.path.join(FRONTEND_STATIC_FOLDER, path)
        if os.path.isfile(static_file_path):
            print(f"Serving Next.js static file: {static_file_path}")
            return send_from_directory(FRONTEND_STATIC_FOLDER, path)
    
    # Direct file match (for other static files)
    static_file_path = os.path.join(FRONTEND_STATIC_FOLDER, path)
    if os.path.isfile(static_file_path):
        print(f"Serving direct file: {static_file_path}")
        return send_from_directory(FRONTEND_STATIC_FOLDER, path)
    
    # Handle directories with trailing slash (e.g., /profile/)
    if path.endswith('/'):
        directory_index_path = os.path.join(FRONTEND_STATIC_FOLDER, path, 'index.html')
        if os.path.isfile(directory_index_path):
            print(f"Serving index.html from directory with trailing slash: {directory_index_path}")
            # Use correct relative path for send_from_directory
            relative_path = os.path.join(path, 'index.html')
            return send_from_directory(FRONTEND_STATIC_FOLDER, relative_path)
    
    # Check if path is a directory without trailing slash and has index.html
    # Handle routes like /profile (without trailing slash)
    if not path.endswith('/'):
        directory_path = os.path.join(FRONTEND_STATIC_FOLDER, path)
        if os.path.isdir(directory_path):
            index_path = os.path.join(directory_path, 'index.html')
            if os.path.isfile(index_path):
                # Instead of redirecting, serve the index.html directly
                print(f"Serving index.html from directory without redirect: {index_path}")
                relative_path = os.path.join(path, 'index.html')
                return send_from_directory(FRONTEND_STATIC_FOLDER, relative_path)
    
    # Fall back to serving index.html for client-side routing
    root_index_path = os.path.join(FRONTEND_STATIC_FOLDER, 'index.html')
    if os.path.isfile(root_index_path):
        print(f"Falling back to root index.html for path: /{path}")
        return send_from_directory(FRONTEND_STATIC_FOLDER, 'index.html')
    
    # If we got here, something is wrong with the static files
    print(f"ERROR: Could not find appropriate file to serve for path: /{path}")
    return jsonify({"error": "File not found"}), 404

# Add a special route for _next/static files
@frontend_bp.route('/_next/<path:filename>')
def serve_next_static(filename):
    print(f"Serving _next file: {filename}")
    path = os.path.join('_next', filename)
    if os.path.isfile(os.path.join(FRONTEND_STATIC_FOLDER, path)):
        return send_from_directory(FRONTEND_STATIC_FOLDER, path)
    return jsonify({"error": "File not found"}), 404

# Add a debug route to check static path configuration
@frontend_bp.route('/api/debug/static-path')
def debug_static_path():
    static_info = {
        "FRONTEND_STATIC_FOLDER": FRONTEND_STATIC_FOLDER,
        "exists": os.path.exists(FRONTEND_STATIC_FOLDER),
        "is_dir": os.path.isdir(FRONTEND_STATIC_FOLDER),
    }
    
    if os.path.exists(FRONTEND_STATIC_FOLDER):
        static_info["contents"] = os.listdir(FRONTEND_STATIC_FOLDER)
        
        # Check if index.html exists
        index_path = os.path.join(FRONTEND_STATIC_FOLDER, 'index.html')
        static_info["index_html_exists"] = os.path.exists(index_path)
        
        # Check _next directory
        next_path = os.path.join(FRONTEND_STATIC_FOLDER, '_next')
        static_info["_next_exists"] = os.path.exists(next_path)
        if os.path.exists(next_path):
            static_info["_next_contents"] = os.listdir(next_path)
    
    return jsonify(static_info)

# Route to test direct file serving
@frontend_bp.route('/api/debug/serve-index')
def debug_serve_index():
    index_path = os.path.join(FRONTEND_STATIC_FOLDER, 'index.html')
    if os.path.isfile(index_path):
        return send_from_directory(FRONTEND_STATIC_FOLDER, 'index.html')
    return jsonify({"error": "index.html not found"}), 404
