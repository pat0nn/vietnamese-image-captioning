from flask import Blueprint, send_from_directory, redirect, jsonify
import os
from app.config.settings import UPLOAD_FOLDER, GCS_ENABLED
from app.utils.db import get_db_connection
from app.utils.cloud_storage import get_image_url

avatar_bp = Blueprint('avatar', __name__)

@avatar_bp.route('/uploads/avatars/<filename>')
@avatar_bp.route('/api/uploads/avatars/<filename>')
def serve_avatar(filename):
    """Serve avatar files from local storage or cloud storage"""
    try:
        if GCS_ENABLED:
            # Kiểm tra xem có phải avatar từ cloud storage không
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Tìm avatar theo tên file trong bảng users
            cursor.execute(
                "SELECT storage_type, avatar FROM users WHERE avatar = %s",
                (filename,)
            )
            
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            # Nếu tìm thấy avatar từ cloud storage
            if result and result[0] == 'gcs':
                # Lấy URL có thời hạn từ Google Cloud Storage
                gcs_path = f"avatars/{result[1]}"
                url = get_image_url(gcs_path)
                return redirect(url)
        
        # Phục vụ từ local storage
        avatar_folder = os.path.join(UPLOAD_FOLDER, 'avatars')
        return send_from_directory(avatar_folder, filename)
    except Exception as e:
        print(f"Error serving avatar: {str(e)}")
        return jsonify({'error': str(e)}), 500
