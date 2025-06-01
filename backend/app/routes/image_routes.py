from flask import Blueprint, request, jsonify, send_from_directory, Response, redirect
import os
import io
import uuid
import base64
import psycopg2
from psycopg2 import errors
from psycopg2.extras import RealDictCursor
from PIL import Image, ExifTags, ImageOps
from flask import Blueprint, request, jsonify
from app.utils.db import get_db_connection
from app.utils.auth import get_current_user, is_admin, token_required
from app.services.model_service import generate_caption
from app.config.settings import UPLOAD_FOLDER, GCS_ENABLED
from app.utils.cloud_storage import upload_image, delete_image, get_image_url, download_image
from app.utils.voice import caption_to_speech
import json
from datetime import date
import piexif

image_bp = Blueprint('image', __name__)

# Add a function to fix image orientation based on EXIF data
def fix_image_orientation(image):
    """
    Fix image orientation based on EXIF data.
    This is particularly important for images taken with mobile phones.
    """
    try:
        # Check if the image has EXIF data
        if hasattr(image, '_getexif') and image._getexif() is not None:
            exif = image._getexif()
            
            # Find the orientation tag (tag 274 in EXIF standard)
            orientation_tag = 274
            
            if orientation_tag in exif:
                orientation = exif[orientation_tag]
                print(f"Found EXIF orientation: {orientation}")
                
                # Apply appropriate transformations based on orientation
                # 1: Normal (no rotation needed)
                # 2: Mirrored horizontally
                # 3: Rotated 180 degrees
                # 4: Mirrored vertically
                # 5: Mirrored horizontally and rotated 270 degrees CW
                # 6: Rotated 90 degrees CW (most common for mobile phones)
                # 7: Mirrored horizontally and rotated 90 degrees CW
                # 8: Rotated 270 degrees CW
                
                if orientation == 1:
                    # Normal orientation, no change needed
                    pass
                elif orientation == 2:
                    # Mirrored horizontally
                    image = image.transpose(Image.FLIP_LEFT_RIGHT)
                elif orientation == 3:
                    # Rotated 180 degrees
                    image = image.rotate(180, expand=True)
                elif orientation == 4:
                    # Mirrored vertically
                    image = image.transpose(Image.FLIP_TOP_BOTTOM)
                elif orientation == 5:
                    # Mirrored horizontally and rotated 270 degrees CW
                    image = image.transpose(Image.FLIP_LEFT_RIGHT)
                    image = image.rotate(270, expand=True)
                elif orientation == 6:
                    # Rotated 90 degrees CW (most common for mobile phones)
                    image = image.rotate(270, expand=True)
                elif orientation == 7:
                    # Mirrored horizontally and rotated 90 degrees CW
                    image = image.transpose(Image.FLIP_LEFT_RIGHT)
                    image = image.rotate(90, expand=True)
                elif orientation == 8:
                    # Rotated 270 degrees CW
                    image = image.rotate(90, expand=True)
                
                print(f"Image orientation corrected from {orientation} to normal")
            else:
                print("No orientation tag found in EXIF data")
        else:
            print("No EXIF data found in image")
            
    except Exception as e:
        print(f"Error fixing image orientation: {str(e)}")
        # Continue with original image if there's an error
        import traceback
        traceback.print_exc()
        
    return image

def save_image_with_correct_orientation(image, output_path):
    """
    Save image with correct orientation and reset the EXIF orientation tag to normal (1).
    This ensures the image is displayed correctly in all viewers.
    """
    try:
        # Check if image has EXIF data
        exif_bytes = None
        if hasattr(image, '_getexif') and image._getexif() is not None:
            # Convert EXIF data to bytes
            exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
            
            # Copy all EXIF data except orientation
            for tag, value in image._getexif().items():
                # Skip the orientation tag (274)
                if tag == 274:
                    continue
                
                # Find which IFD this tag belongs to
                ifd = "0th"
                if tag in piexif.ExifIFD.__dict__.values():
                    ifd = "Exif"
                elif tag in piexif.GPSIFD.__dict__.values():
                    ifd = "GPS"
                
                # Add the tag to the appropriate IFD
                if isinstance(value, bytes):
                    exif_dict[ifd][tag] = value
                else:
                    try:
                        # Try to convert the value to bytes if needed
                        exif_dict[ifd][tag] = value
                    except:
                        # Skip tags that can't be converted
                        pass
            
            # Set orientation to normal (1)
            exif_dict["0th"][274] = 1
            
            # Convert to bytes
            try:
                exif_bytes = piexif.dump(exif_dict)
            except:
                print("Error dumping EXIF data, saving without EXIF")
                exif_bytes = None
        
        # Save the image with the updated EXIF data
        if exif_bytes:
            image.save(output_path, exif=exif_bytes, quality=95)
            print(f"Image saved with normalized EXIF orientation to {output_path}")
        else:
            image.save(output_path, quality=95)
            print(f"Image saved without EXIF data to {output_path}")
            
    except Exception as e:
        print(f"Error saving image with correct orientation: {str(e)}")
        # Fall back to regular save
        try:
            image.save(output_path, quality=95)
            print(f"Fallback: Image saved without EXIF to {output_path}")
        except Exception as save_error:
            print(f"Critical error saving image: {str(save_error)}")
            raise

def track_activity(activity_type, user_id=None, details=None):
    """
    Track user activity in the database
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        ip_address = request.remote_addr
        
        # Convert details to JSON if provided
        json_details = None
        if details:
            json_details = json.dumps(details)
        
        cursor.execute(
            """
            INSERT INTO user_activities (activity_type, user_id, ip_address, details)
            VALUES (%s, %s, %s, %s)
            """,
            (activity_type, user_id, ip_address, json_details)
        )
        
        # Update daily stats
        today = date.today().isoformat()
        
        # Try to update existing record for today
        if activity_type == 'visit':
            cursor.execute(
                """
                UPDATE daily_stats SET visits = visits + 1
                WHERE date = %s
                """,
                (today,)
            )
        elif activity_type == 'caption':
            cursor.execute(
                """
                UPDATE daily_stats SET caption_requests = caption_requests + 1
                WHERE date = %s
                """,
                (today,)
            )
        elif activity_type == 'contribution':
            cursor.execute(
                """
                UPDATE daily_stats SET contributions = contributions + 1
                WHERE date = %s
                """,
                (today,)
            )
        
        # If no record exists for today, create one
        if cursor.rowcount == 0:
            if activity_type == 'visit':
                cursor.execute(
                    """
                    INSERT INTO daily_stats (date, visits)
                    VALUES (%s, 1)
                    """,
                    (today,)
                )
            elif activity_type == 'caption':
                cursor.execute(
                    """
                    INSERT INTO daily_stats (date, caption_requests)
                    VALUES (%s, 1)
                    """,
                    (today,)
                )
            elif activity_type == 'contribution':
                cursor.execute(
                    """
                    INSERT INTO daily_stats (date, contributions)
                    VALUES (%s, 1)
                    """,
                    (today,)
                )
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error tracking activity: {str(e)}")

@image_bp.route('/caption', methods=['POST'])
@image_bp.route('/api/caption', methods=['POST'])
def caption_image():
    print(f"Received caption request at {request.path}")
    
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    
    # Get user ID if logged in
    user_data = get_current_user(request)
    user_id = user_data['id'] if user_data else None
    
    file = request.files['image']
    
    try:
        # Read and convert image
        print("Reading image data...")
        image_bytes = file.read()
        image = Image.open(io.BytesIO(image_bytes))
        print("Image successfully loaded")
        
        # Fix image orientation based on EXIF data
        print("Fixing image orientation...")
        image = fix_image_orientation(image)
        # Convert to RGB after fixing orientation (some images might be RGBA or other formats)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        print("Image orientation fixed and converted to RGB")
        
        # Generate caption
        print("Generating caption...")
        ai_caption = generate_caption(image)
        print(f"Caption generated: {ai_caption}")
        
        # Check if caption was generated successfully
        if ai_caption is None:
            print("Failed to generate caption")
            return jsonify({'error': 'Không thể tạo caption cho hình ảnh này'}), 500
            
        # Generate audio for the caption
        print(f"Generating audio for caption: {ai_caption}")
        try:
            audio_data = caption_to_speech(ai_caption)
            print(f"Audio generation status: {'Success' if audio_data else 'Failed'}")
        except Exception as audio_error:
            print(f"Error generating audio: {str(audio_error)}")
            audio_data = None
        
        # Create response data
        response_data = {
            'success': True
        }
        
        # Only include caption if audio was successfully generated
        if audio_data:
            audio_data_base64 = base64.b64encode(audio_data).decode('utf-8')
            print(f"Audio generated successfully, size: {len(audio_data_base64)} bytes")
            response_data['audio'] = audio_data_base64
            response_data['caption'] = ai_caption
            print("Caption and audio ready to be sent to frontend")
        else:
            print("Failed to generate audio for caption")
            return jsonify({'error': 'Không thể tạo file âm thanh cho caption'}), 500
        
        # Lưu ảnh vào storage (local hoặc cloud)
        image_id = str(uuid.uuid4())
        print(f"Generated image ID: {image_id}")
        
        try:
            if GCS_ENABLED:
                # Upload ảnh lên Google Cloud Storage
                print("Uploading image to Google Cloud Storage...")
                image_id, gcs_path, public_url = upload_image(image, f"{image_id}.jpg")
                print(f"Image uploaded to GCS: {gcs_path}")
            else:
                # Save image to local disk
                print("Saving image to local storage...")
                filename = f"{image_id}.jpg"
                image_path = os.path.join(UPLOAD_FOLDER, filename)
                save_image_with_correct_orientation(image, image_path)
                gcs_path = filename  # Trong trường hợp local, đây là tên file
                print(f"Image saved to local path: {image_path}")
        except Exception as storage_error:
            print(f"Error saving image to storage: {str(storage_error)}")
            # Return caption even if storage fails
            response_data['caption'] = ai_caption
            return jsonify(response_data), 200
        
        # Save to database with just AI caption
        print("Connecting to database...")
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Thêm xử lý trùng lặp ID
        max_attempts = 3
        attempt = 0
        inserted = False
        
        print("Attempting to insert record into database...")
        while attempt < max_attempts and not inserted:
            try:
                cursor.execute(
                    """
                    INSERT INTO images (image_id, image_path, ai_caption, user_id, storage_type)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (image_id, gcs_path, ai_caption, user_id, 'gcs' if GCS_ENABLED else 'local')
                )
                
                new_id = cursor.fetchone()[0]
                inserted = True
                print(f"Database record inserted successfully, ID: {new_id}")
            except psycopg2.errors.UniqueViolation as db_error:
                # Nếu có lỗi trùng khóa, rollback và thử lại
                conn.rollback()
                attempt += 1
                print(f"Duplicate key detected, retrying... (attempt {attempt}/{max_attempts}): {str(db_error)}")
                
                # Cập nhật sequence để tránh trùng lặp
                cursor.execute("SELECT MAX(id) FROM images")
                max_id = cursor.fetchone()[0]
                if max_id:
                    cursor.execute(f"ALTER SEQUENCE images_id_seq RESTART WITH {max_id + 1}")
                    conn.commit()
            except Exception as general_db_error:
                print(f"Database error: {str(general_db_error)}")
                conn.rollback()
                raise
        
        if not inserted:
            print("Failed to insert record after multiple attempts")
            cursor.close()
            conn.close()
            return jsonify({'error': 'Không thể lưu ảnh vào cơ sở dữ liệu sau nhiều lần thử'}), 500
        
        cursor.close()
        conn.close()
        print("Database connection closed")
        
        # Add image_id to response
        response_data['image_id'] = image_id
        
        # Track this activity
        try:
            print("Tracking activity...")
            details = {'image_id': image_id}
            track_activity('caption', user_id, details)
            print("Activity tracked successfully")
        except Exception as tracking_error:
            print(f"Error tracking activity: {str(tracking_error)}")
            # Continue even if tracking fails
        
        print("Returning successful response")
        return jsonify(response_data)
    
    except Exception as e:
        print(f"Error generating caption: {str(e)}")
        # Print full stack trace for debugging
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@image_bp.route('/contribute', methods=['POST'])
@image_bp.route('/api/contribute', methods=['POST'])
@token_required
def contribute_data(user_data):
    user_id = user_data['id']
    
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    
    file = request.files['image']
    user_caption = request.form.get('userCaption', '')
    skip_ai_caption = request.form.get('skipAiCaption', 'false').lower() == 'true'
    
    try:
        # Read and convert image
        image_bytes = file.read()
        image = Image.open(io.BytesIO(image_bytes))
        
        # Fix image orientation based on EXIF data
        image = fix_image_orientation(image)
        # Convert to RGB after fixing orientation
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Generate AI caption only if not skipped
        ai_caption = None
        if not skip_ai_caption:
            ai_caption = generate_caption(image)
        
        # Lưu ảnh vào storage (local hoặc cloud)
        image_id = str(uuid.uuid4())
        
        if GCS_ENABLED:
            # Upload ảnh lên Google Cloud Storage
            image_id, gcs_path, public_url = upload_image(image, f"{image_id}.jpg")
        else:
            # Save image to local disk
            filename = f"{image_id}.jpg"
            image_path = os.path.join(UPLOAD_FOLDER, filename)
            save_image_with_correct_orientation(image, image_path)
            gcs_path = filename  # Trong trường hợp local, đây là tên file
        
        # Save to database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Thêm xử lý trùng lặp ID
        max_attempts = 3
        attempt = 0
        inserted = False
        image_id_inserted = None
        
        while attempt < max_attempts and not inserted:
            try:
                cursor.execute(
                    """
                    INSERT INTO images (image_id, image_path, user_caption, ai_caption, user_id, storage_type)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (image_id, gcs_path, user_caption, ai_caption, user_id, 'gcs' if GCS_ENABLED else 'local')
                )
                
                image_id_inserted = cursor.fetchone()[0]
                inserted = True
            except psycopg2.errors.UniqueViolation:
                # Nếu có lỗi trùng khóa, rollback và thử lại
                conn.rollback()
                attempt += 1
                print(f"Duplicate key detected, retrying... (attempt {attempt}/{max_attempts})")
                
                # Cập nhật sequence để tránh trùng lặp
                cursor.execute("SELECT MAX(id) FROM images")
                max_id = cursor.fetchone()[0]
                if max_id:
                    cursor.execute(f"ALTER SEQUENCE images_id_seq RESTART WITH {max_id + 1}")
                    conn.commit()
        
        if not inserted:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Không thể lưu ảnh vào cơ sở dữ liệu sau nhiều lần thử'}), 500
        
        # Add record to contributions table
        cursor.execute(
            """
            INSERT INTO contributions (user_id, image_id, status)
            VALUES (%s, %s, %s)
            RETURNING id
            """,
            (user_id, image_id, "pending")
        )
        
        contribution_id = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        # Track this activity
        details = {'image_id': image_id, 'contribution_id': contribution_id}
        track_activity('contribution', user_id, details)
        
        return jsonify({
            'success': True,
            'id': image_id_inserted,
            'image_id': image_id,
            'contribution_id': contribution_id,
            'user_caption': user_caption,
            'ai_caption': ai_caption
        })
        
    except Exception as e:
        print(f"Error saving contribution: {str(e)}")
        return jsonify({'error': str(e)}), 500

@image_bp.route('/contributions', methods=['GET'])
@image_bp.route('/api/contributions', methods=['GET'])
def get_contributions():
    try:
        # Get optional status filter
        status = request.args.get('status', None)
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        query = """
            SELECT c.id as contribution_id, c.status, c.review_notes, 
                   i.*, u.username as contributor,
                   r.username as reviewer_name
            FROM contributions c
            JOIN images i ON c.image_id = i.image_id
            LEFT JOIN users u ON c.user_id = u.id
            LEFT JOIN users r ON c.reviewer_id = r.id
        """
        
        params = []
        if status:
            query += " WHERE c.status = %s"
            params.append(status)
            
        query += " ORDER BY c.created_at DESC"
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
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

@image_bp.route('/user/contributions', methods=['GET'])
@image_bp.route('/api/user/contributions', methods=['GET'])
@token_required
def get_user_contributions(user_data):
    user_id = user_data['id']
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute("""
            SELECT c.id as contribution_id, c.status, c.review_notes, i.*
            FROM contributions c
            JOIN images i ON c.image_id = i.image_id
            WHERE c.user_id = %s
            ORDER BY c.created_at DESC
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

@image_bp.route('/contribution/<image_id>', methods=['PUT'])
@image_bp.route('/api/contribution/<image_id>', methods=['PUT'])
@image_bp.route('/api/user/contribution/<image_id>', methods=['PUT'])
@token_required
def update_contribution(user_data, image_id):
    user_id = user_data['id']
    data = request.json
    user_caption = data.get('userCaption', '')
    ai_caption = data.get('aiCaption')
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if the user is an admin
        admin_status = is_admin(user_id)
        
        if admin_status:
            # Admins can edit any image
            cursor.execute("SELECT id FROM images WHERE image_id = %s", (image_id,))
        else:
            # Regular users can only edit their own images
            cursor.execute("""
                SELECT id FROM images 
                WHERE image_id = %s AND user_id = %s
            """, (image_id, user_id))
        
        image = cursor.fetchone()
        if not image:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Image not found or you do not have permission'}), 404
        
        # Build the update query dynamically based on what fields are provided
        update_fields = []
        params = []
        
        if user_caption is not None:
            update_fields.append("user_caption = %s")
            params.append(user_caption)
        
        # Only admins can update AI caption
        if admin_status and ai_caption is not None:
            update_fields.append("ai_caption = %s")
            params.append(ai_caption)
        
        if not update_fields:
            cursor.close()
            conn.close()
            return jsonify({'error': 'No fields to update'}), 400
        
        # Update the caption
        params.append(image_id)
        cursor.execute(f"""
            UPDATE images 
            SET {', '.join(update_fields)} 
            WHERE image_id = %s
            RETURNING id
        """, params)
        
        updated_id = cursor.fetchone()[0]
        
        # Update contribution status if provided and user is admin
        if admin_status and 'status' in data:
            status = data.get('status')
            review_notes = data.get('reviewNotes', '')
            
            cursor.execute("""
                UPDATE contributions 
                SET status = %s, reviewer_id = %s, review_notes = %s, updated_at = CURRENT_TIMESTAMP
                WHERE image_id = %s
                RETURNING id
            """, (status, user_id, review_notes, image_id))
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'id': updated_id,
            'message': 'Contribution updated successfully'
        })
        
    except Exception as e:
        print(f"Error updating contribution: {str(e)}")
        return jsonify({'error': str(e)}), 500

@image_bp.route('/contribution/<image_id>', methods=['DELETE'])
@image_bp.route('/api/contribution/<image_id>', methods=['DELETE'])
@image_bp.route('/api/user/contribution/<image_id>', methods=['DELETE'])
@token_required
def delete_contribution(user_data, image_id):
    user_id = user_data['id']
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if the user is an admin
        admin_status = is_admin(user_id)
        
        if admin_status:
            # Admins can delete any image
            cursor.execute("""
                SELECT i.image_path, i.storage_type, c.id
                FROM images i
                JOIN contributions c ON i.image_id = c.image_id
                WHERE i.image_id = %s
            """, (image_id,))
        else:
            # Regular users can only delete their own images
            cursor.execute("""
                SELECT i.image_path, i.storage_type, c.id 
                FROM images i
                JOIN contributions c ON i.image_id = c.image_id
                WHERE i.image_id = %s AND c.user_id = %s
            """, (image_id, user_id))
        
        image_result = cursor.fetchone()
        if not image_result:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Image not found or you do not have permission'}), 404
            
        image_path = image_result[0]
        storage_type = image_result[1]
        contribution_id = image_result[2]
        
        # Delete the image file
        if storage_type == 'gcs' and GCS_ENABLED:
            # Delete from Google Cloud Storage
            delete_image(image_path)
        else:
            # Delete from local storage
            local_path = os.path.join(UPLOAD_FOLDER, image_path)
            if os.path.exists(local_path):
                os.remove(local_path)
        
        # Delete the database entries
        cursor.execute("DELETE FROM contributions WHERE image_id = %s", (image_id,))
        cursor.execute("DELETE FROM caption_ratings WHERE image_id = %s", (image_id,))
        cursor.execute("DELETE FROM images WHERE image_id = %s", (image_id,))
        
        cursor.close()
        conn.close()
        
        # Track this activity
        details = {'image_id': image_id, 'contribution_id': contribution_id}
        track_activity('delete_contribution', user_id, details)
        
        return jsonify({
            'success': True,
            'message': 'Contribution deleted successfully'
        })
        
    except Exception as e:
        print(f"Error deleting contribution: {str(e)}")
        return jsonify({'error': str(e)}), 500

@image_bp.route('/contribution/id/<contribution_id>', methods=['DELETE'])
@image_bp.route('/api/contribution/id/<contribution_id>', methods=['DELETE'])
@token_required
def delete_contribution_by_id(user_data, contribution_id):
    return _delete_contribution_by_id_helper(user_data, contribution_id)

# Hàm helper không có decorator để xử lý logic xóa contribution
def _delete_contribution_by_id_helper(user_data, contribution_id):
    user_id = user_data['id']
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if the user is an admin
        admin_status = is_admin(user_id)
        
        # First, get the image_id and other details from the contribution_id
        if admin_status:
            # Admins can delete any contribution
            cursor.execute("""
                SELECT c.image_id, i.image_path, i.storage_type
                FROM contributions c
                JOIN images i ON c.image_id = i.image_id
                WHERE c.id = %s
            """, (contribution_id,))
        else:
            # Regular users can only delete their own contributions
            cursor.execute("""
                SELECT c.image_id, i.image_path, i.storage_type
                FROM contributions c
                JOIN images i ON c.image_id = i.image_id
                WHERE c.id = %s AND c.user_id = %s
            """, (contribution_id, user_id))
        
        result = cursor.fetchone()
        if not result:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Contribution not found or you do not have permission'}), 404
            
        image_id = result[0]
        image_path = result[1]
        storage_type = result[2]
        
        # Delete the image file
        if storage_type == 'gcs' and GCS_ENABLED:
            # Delete from Google Cloud Storage
            delete_image(image_path)
        else:
            # Delete from local storage
            local_path = os.path.join(UPLOAD_FOLDER, image_path)
            if os.path.exists(local_path):
                os.remove(local_path)
        
        # Delete the database entries
        cursor.execute("DELETE FROM contributions WHERE id = %s", (contribution_id,))
        cursor.execute("DELETE FROM caption_ratings WHERE image_id = %s", (image_id,))
        cursor.execute("DELETE FROM images WHERE image_id = %s", (image_id,))
        
        cursor.close()
        conn.close()
        
        # Track this activity
        details = {'image_id': image_id, 'contribution_id': contribution_id}
        track_activity('delete_contribution', user_id, details)
        
        return jsonify({
            'success': True,
            'message': 'Contribution deleted successfully'
        })
        
    except Exception as e:
        print(f"Error deleting contribution: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Endpoint để xóa contribution theo contribution_id (không có tiền tố id/)
@image_bp.route('/api/contribution/<int:contribution_id>', methods=['DELETE'])
@token_required
def delete_contribution_direct(user_data, contribution_id):
    # Gọi hàm helper
    return _delete_contribution_by_id_helper(user_data, contribution_id)

@image_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    """Phục vụ file từ local storage hoặc redirect đến Cloud Storage"""
    try:
        # Kiểm tra xem file có phải là từ cloud storage hay không
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Tìm ảnh theo tên file
        cursor.execute(
            "SELECT storage_type, image_path FROM images WHERE image_path = %s OR image_path LIKE %s",
            (filename, f"%/{filename}")
        )
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        # Nếu tìm thấy ảnh và là cloud storage
        if result and result[0] == 'gcs' and GCS_ENABLED:
            # Lấy URL có thời hạn từ Google Cloud Storage
            url = get_image_url(result[1])
            return redirect(url)
        else:
            # Phục vụ từ local storage
            return send_from_directory(UPLOAD_FOLDER, filename)
    except Exception as e:
        print(f"Error serving file: {str(e)}")
        return jsonify({'error': str(e)}), 500

@image_bp.route('/api/uploads/<filename>')
def api_uploaded_file(filename):
    """API endpoint để phục vụ file từ local storage hoặc cloud storage"""
    try:
        # Kiểm tra xem file có phải là từ cloud storage hay không
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Tìm ảnh theo tên file
        cursor.execute(
            "SELECT storage_type, image_path FROM images WHERE image_path = %s OR image_path LIKE %s",
            (filename, f"%/{filename}")
        )
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        # Nếu tìm thấy ảnh và là cloud storage
        if result and result[0] == 'gcs' and GCS_ENABLED:
            # Lấy URL có thời hạn từ Google Cloud Storage
            url = get_image_url(result[1])
            return redirect(url)
        else:
            # Phục vụ từ local storage
            return send_from_directory(UPLOAD_FOLDER, filename)
    except Exception as e:
        print(f"Error serving file: {str(e)}")
        return jsonify({'error': str(e)}), 500

@image_bp.route('/rate/<image_id>', methods=['POST'])
@image_bp.route('/api/rate/<image_id>', methods=['POST'])
def rate_caption(image_id):
    # Get user data if logged in
    user_data = get_current_user(request)
    user_id = user_data['id'] if user_data else None
    
    data = request.json
    rating = data.get('rating')
    
    if not rating or not isinstance(rating, int) or rating < 1 or rating > 5:
        return jsonify({'error': 'Invalid rating value. Must be an integer between 1 and 5'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if image exists
        cursor.execute("SELECT id FROM images WHERE image_id = %s", (image_id,))
        image = cursor.fetchone()
        if not image:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Image not found'}), 404
        
        # Check if user has already rated this image
        if user_id:
            cursor.execute(
                "SELECT id FROM caption_ratings WHERE image_id = %s AND user_id = %s",
                (image_id, user_id)
            )
            existing_rating = cursor.fetchone()
            
            if existing_rating:
                # Update existing rating
                cursor.execute(
                    "UPDATE caption_ratings SET rating = %s WHERE image_id = %s AND user_id = %s",
                    (rating, image_id, user_id)
                )
            else:
                # Insert new rating
                cursor.execute(
                    "INSERT INTO caption_ratings (image_id, user_id, rating) VALUES (%s, %s, %s)",
                    (image_id, user_id, rating)
                )
        else:
            # Anonymous rating (only IP-based)
            cursor.execute(
                "INSERT INTO caption_ratings (image_id, rating) VALUES (%s, %s)",
                (image_id, rating)
            )
        
        # Update daily stats for ratings
        today = date.today().isoformat()
        
        cursor.execute(
            """
            UPDATE daily_stats 
            SET ratings = ratings + 1, ratings_sum = ratings_sum + %s
            WHERE date = %s
            """,
            (rating, today)
        )
        
        # If no record exists for today, create one
        if cursor.rowcount == 0:
            cursor.execute(
                """
                INSERT INTO daily_stats (date, ratings, ratings_sum)
                VALUES (%s, 1, %s)
                """,
                (today, rating)
            )
        
        cursor.close()
        conn.close()
        
        # Track this activity
        details = {'image_id': image_id, 'rating': rating}
        track_activity('rating', user_id, details)
        
        return jsonify({
            'success': True,
            'message': 'Rating submitted successfully'
        })
        
    except Exception as e:
        print(f"Error submitting rating: {str(e)}")
        return jsonify({'error': str(e)}), 500

@image_bp.route('/ratings/<image_id>', methods=['GET'])
@image_bp.route('/api/ratings/<image_id>', methods=['GET'])
def get_ratings(image_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Check if image exists
        cursor.execute("SELECT id FROM images WHERE image_id = %s", (image_id,))
        image = cursor.fetchone()
        if not image:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Image not found'}), 404
        
        # Get average rating and count
        cursor.execute(
            """
            SELECT 
                COUNT(*) as rating_count, 
                AVG(rating) as average_rating,
                SUM(CASE WHEN rating = 1 THEN 1 ELSE 0 END) as rating_1,
                SUM(CASE WHEN rating = 2 THEN 1 ELSE 0 END) as rating_2,
                SUM(CASE WHEN rating = 3 THEN 1 ELSE 0 END) as rating_3,
                SUM(CASE WHEN rating = 4 THEN 1 ELSE 0 END) as rating_4,
                SUM(CASE WHEN rating = 5 THEN 1 ELSE 0 END) as rating_5
            FROM caption_ratings
            WHERE image_id = %s
            """,
            (image_id,)
        )
        
        rating_stats = cursor.fetchone()
        
        # Get user's rating if logged in
        user_data = get_current_user(request)
        user_rating = None
        
        if user_data:
            user_id = user_data['id']
            cursor.execute(
                "SELECT rating FROM caption_ratings WHERE image_id = %s AND user_id = %s",
                (image_id, user_id)
            )
            result = cursor.fetchone()
            if result:
                user_rating = result['rating']
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'stats': rating_stats,
            'user_rating': user_rating
        })
        
    except Exception as e:
        print(f"Error getting ratings: {str(e)}")
        return jsonify({'error': str(e)}), 500

@image_bp.route('/stats', methods=['GET'])
@image_bp.route('/api/stats', methods=['GET'])
def get_stats():
    # Check admin permissions
    user_data = get_current_user(request)
    if not user_data:
        return jsonify({'error': 'Authentication required'}), 401
        
    user_id = user_data['id']
    if not is_admin(user_id):
        return jsonify({'error': 'Admin privileges required'}), 403
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Get date range from request (optional)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = """
            SELECT 
                date, 
                visits, 
                caption_requests, 
                contributions, 
                ratings, 
                ratings_sum,
                CASE 
                    WHEN ratings > 0 THEN ratings_sum / ratings::float
                    ELSE 0
                END as average_rating
            FROM daily_stats
        """
        
        params = []
        has_where = False
        
        if start_date:
            query += " WHERE date >= %s"
            params.append(start_date)
            has_where = True
            
        if end_date:
            if has_where:
                query += " AND date <= %s"
            else:
                query += " WHERE date <= %s"
            params.append(end_date)
            
        query += " ORDER BY date DESC"
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        stats = cursor.fetchall()
        
        # Get summary statistics
        cursor.execute("""
            SELECT 
                SUM(visits) as total_visits,
                SUM(caption_requests) as total_captions,
                SUM(contributions) as total_contributions,
                SUM(ratings) as total_ratings,
                CASE 
                    WHEN SUM(ratings) > 0 THEN SUM(ratings_sum) / SUM(ratings)::float
                    ELSE 0
                END as overall_average_rating
            FROM daily_stats
        """)
        
        summary = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'daily_stats': stats,
            'summary': summary
        })
        
    except Exception as e:
        print(f"Error getting stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@image_bp.route('/caption-history', methods=['GET'])
@image_bp.route('/api/caption-history', methods=['GET'])
def get_caption_history():
    try:
        # Check for admin access
        user_data = get_current_user(request)
        if not user_data:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Handle legacy token format - if 'id' is missing but 'sub' is present
        if 'id' not in user_data and 'sub' in user_data:
            user_data['id'] = user_data['sub']
            print(f"Converted legacy token format: copied 'sub' key ({user_data['sub']}) to 'id' key")
            
        user_id = user_data.get('id')
        if not user_id:
            return jsonify({'error': 'Invalid token: missing user ID'}), 401
            
        if not is_admin(user_id):
            return jsonify({'error': 'Admin privileges required'}), 403
            
        # Parse query parameters
        page = int(request.args.get('page', 1))
        limit = min(int(request.args.get('limit', 20)), 100)  # Cap at 100
        user_filter_id = request.args.get('user_id')
        ai_only = request.args.get('ai_only', '').lower() in ['true', '1', 'yes']
        rating_filter = request.args.get('rating')
        if rating_filter and rating_filter.isdigit():
            rating_filter = int(rating_filter)
        else:
            rating_filter = None
        offset = (page - 1) * limit
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Base query for images with their captions and ratings
        query = """
            SELECT 
                i.image_id, i.image_path, i.ai_caption, i.user_caption, i.created_at,
                u.username, u.id as user_id,
                COALESCE(AVG(cr.rating), 0) as average_rating,
                COUNT(cr.id) as rating_count
            FROM images i
            LEFT JOIN users u ON i.user_id = u.id
            LEFT JOIN caption_ratings cr ON i.image_id = cr.image_id
        """
        
        # Count query for pagination
        count_query = """
            SELECT COUNT(*) as total
            FROM images i
            LEFT JOIN (
                SELECT image_id, COALESCE(AVG(rating), 0) as avg_rating, COUNT(id) as rating_count
                FROM caption_ratings
                GROUP BY image_id
            ) cr ON i.image_id = cr.image_id
        """
        
        # Add condition for specific user if requested
        params = []
        where_added = False
        
        if user_filter_id:
            query += " WHERE i.user_id = %s"
            count_query += " WHERE i.user_id = %s"
            params.append(user_filter_id)
            where_added = True
        
        # Add condition to filter by ai_caption if ai_only is true
        if ai_only:
            if where_added:
                query += " AND i.ai_caption IS NOT NULL AND i.ai_caption != ''"
                count_query += " AND i.ai_caption IS NOT NULL AND i.ai_caption != ''"
            else:
                query += " WHERE i.ai_caption IS NOT NULL AND i.ai_caption != ''"
                count_query += " WHERE i.ai_caption IS NOT NULL AND i.ai_caption != ''"
                where_added = True
        
        # Add condition to filter by rating if requested
        if rating_filter is not None:
            # We need to have the rating aggregation before WHERE
            having_clause = " HAVING ROUND(COALESCE(AVG(cr.rating), 0)) = %s"
            params.append(rating_filter)
            
            # Update count query to also filter by rating
            if where_added:
                count_query += " AND ROUND(cr.avg_rating) = %s"
            else:
                count_query += " WHERE ROUND(cr.avg_rating) = %s"
            # Add parameter for count query
            
        # Group by to aggregate ratings
        query += """
            GROUP BY i.image_id, i.image_path, i.ai_caption, i.user_caption, i.created_at, u.username, u.id
        """
        
        # Add HAVING clause after GROUP BY if rating filter is applied
        if rating_filter is not None:
            query += having_clause
        
        # Add ORDER BY and pagination
        query += """
            ORDER BY i.created_at DESC
            LIMIT %s OFFSET %s
        """
        
        # Add pagination parameters
        pagination_params = params.copy()
        pagination_params.extend([limit, offset])
        
        # Execute count query to get total
        cursor.execute(count_query, params)
        total_result = cursor.fetchone()
        total = total_result['total'] if total_result else 0
        
        # Execute main query with pagination
        cursor.execute(query, pagination_params)
        captions = cursor.fetchall()
        
        # Get user's own ratings
        if user_id and captions:
            # Get image IDs from the results
            image_ids = [caption['image_id'] for caption in captions]
            
            if image_ids:
                placeholders = ','.join(['%s'] * len(image_ids))
                
                # Query user's ratings for these images
                user_ratings_query = f"""
                    SELECT image_id, rating 
                    FROM caption_ratings
                    WHERE user_id = %s AND image_id IN ({placeholders})
                """
                
                user_ratings_params = [user_id] + image_ids
                cursor.execute(user_ratings_query, user_ratings_params)
                user_ratings = {row['image_id']: row['rating'] for row in cursor.fetchall()}
                
                # Add user's rating to each caption
                for caption in captions:
                    caption['user_rating'] = user_ratings.get(caption['image_id'])
        
        cursor.close()
        conn.close()
        
        # Convert timestamps to ISO format for JSON
        for caption in captions:
            if caption.get('created_at'):
                caption['created_at'] = caption['created_at'].isoformat()
        
        return jsonify({
            'success': True,
            'captions': captions,
            'total': total,
            'page': page,
            'limit': limit,
            'pages': (total + limit - 1) // limit  # Ceiling division
        })
        
    except Exception as e:
        print(f"Error retrieving caption history: {str(e)}")
        return jsonify({'error': str(e)}), 500
