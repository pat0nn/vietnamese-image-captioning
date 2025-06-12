from flask import Blueprint, request, jsonify, send_from_directory, session
from app.utils.db import get_db_connection
from app.utils.auth import get_current_user, is_admin, token_required
from app.services.model_service import load_model
from app.config.settings import MODEL_PATH, UPLOAD_FOLDER, GCS_ENABLED
from app.utils.cloud_storage import download_image
import psycopg2.extras
import bcrypt
from datetime import datetime, timedelta
from app.models.user import User
import os
import json
import zipfile
import tempfile
import io
from app.utils.activity_tracker import track_activity

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """
    Decorator to check if user is an admin
    """
    from functools import wraps
    
    @wraps(f)
    @token_required
    def decorated_function(user_data, *args, **kwargs):
        # Ensure the token format is handled correctly
        if 'id' not in user_data and 'sub' in user_data:
            user_data['id'] = user_data['sub']
            print(f"Converted legacy token format in admin_required: copied 'sub' key ({user_data['sub']}) to 'id' key")
        
        # Now get the user ID safely
        user_id = user_data.get('id')
        if not user_id:
            return jsonify({'error': 'Invalid token: missing user ID'}), 401
            
        if not is_admin(user_id):
            return jsonify({'error': 'Admin privileges required'}), 403
        return f(user_data, *args, **kwargs)
    
    return decorated_function

@admin_bp.route('/admin/check', methods=['GET'])
@admin_bp.route('/api/admin/check', methods=['GET'])
@token_required
def check_admin(user_data):
    user_id = user_data['id']
    admin_status = is_admin(user_id)
    
    return jsonify({
        'success': True,
        'isAdmin': admin_status
    })

@admin_bp.route('/admin/model-versions', methods=['GET'])
@admin_bp.route('/api/admin/model-versions', methods=['GET'])
@admin_required
def get_model_versions(user_data):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute("""
            SELECT * FROM model_versions
            ORDER BY created_at DESC
        """)
        versions = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'versions': versions
        })
        
    except Exception as e:
        print(f"Error getting model versions: {str(e)}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/admin/model-versions', methods=['POST'])
@admin_bp.route('/api/admin/model-versions', methods=['POST'])
@admin_required
def add_model_version(user_data):
    data = request.json
    version_name = data.get('versionName')
    model_path = data.get('modelPath')
    description = data.get('description', '')
    is_active = data.get('isActive', False)
    
    if not version_name or not model_path:
        return jsonify({'error': 'Version name and model path are required'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # If this version is set as active, deactivate all other versions first
        if is_active:
            cursor.execute("UPDATE model_versions SET is_active = FALSE")
        
        cursor.execute("""
            INSERT INTO model_versions (version_name, model_path, is_active, description)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (version_name, model_path, is_active, description))
        
        new_id = cursor.fetchone()[0]
        
        # If this is the active version, update the global MODEL_PATH
        if is_active:
            global MODEL_PATH
            MODEL_PATH = model_path
            # Reload the model with the new path
            load_model()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'id': new_id,
            'message': 'Model version added successfully'
        })
        
    except Exception as e:
        print(f"Error adding model version: {str(e)}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/admin/model-versions/<int:version_id>', methods=['PUT'])
@admin_bp.route('/api/admin/model-versions/<int:version_id>', methods=['PUT'])
@admin_required
def update_model_version(version_id, user_data):
    data = request.json
    version_name = data.get('versionName')
    model_path = data.get('modelPath')
    description = data.get('description')
    is_active = data.get('isActive')
    
    update_fields = []
    params = []
    
    if version_name is not None:
        update_fields.append("version_name = %s")
        params.append(version_name)
    
    if model_path is not None:
        update_fields.append("model_path = %s")
        params.append(model_path)
    
    if description is not None:
        update_fields.append("description = %s")
        params.append(description)
    
    if is_active is not None:
        update_fields.append("is_active = %s")
        params.append(is_active)
    
    if not update_fields:
        return jsonify({'error': 'No fields to update'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # If this version is being set as active, deactivate all other versions first
        if is_active:
            cursor.execute("UPDATE model_versions SET is_active = FALSE")
        
        # Update the specified version
        query = f"UPDATE model_versions SET {', '.join(update_fields)} WHERE id = %s RETURNING id, model_path, is_active"
        params.append(version_id)
        
        cursor.execute(query, params)
        result = cursor.fetchone()
        
        if not result:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Model version not found'}), 404
        
        updated_id, updated_model_path, updated_is_active = result
        
        # If this is now the active version, update the global MODEL_PATH
        if updated_is_active:
            global MODEL_PATH
            MODEL_PATH = updated_model_path
            # Reload the model with the new path
            load_model()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'id': updated_id,
            'message': 'Model version updated successfully'
        })
        
    except Exception as e:
        print(f"Error updating model version: {str(e)}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/admin/model-versions/<int:version_id>', methods=['DELETE'])
@admin_bp.route('/api/admin/model-versions/<int:version_id>', methods=['DELETE'])
@admin_required
def delete_model_version(version_id, user_data):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if the version exists and is active
        cursor.execute("SELECT is_active FROM model_versions WHERE id = %s", (version_id,))
        result = cursor.fetchone()
        
        if not result:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Model version not found'}), 404
        
        is_active = result[0]
        
        # Don't allow deleting the active version
        if is_active:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Cannot delete the active model version'}), 400
        
        # Delete the version
        cursor.execute("DELETE FROM model_versions WHERE id = %s", (version_id,))
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Model version deleted successfully'
        })
        
    except Exception as e:
        print(f"Error deleting model version: {str(e)}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/admin/users', methods=['GET']) 
@admin_bp.route('/api/admin/users', methods=['GET'])
@admin_required
def get_users(user_data):
    try:
        # Parse query parameters
        page = int(request.args.get('page', 1))
        limit = min(int(request.args.get('limit', 20)), 100)  # Cap at 100
        search = request.args.get('search', '')
        offset = (page - 1) * limit
        
        # If search is provided, get filtered results
        if search:
            # User.search returns a tuple of (users, total_count)
            # This method handles its own database connection
            users_result, search_count = User.search(search, limit, offset)
            users = users_result
            total_count = search_count
        else:
            # Get all users with pagination
            users = User.get_all()
            
            # Get total count for pagination
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            total_count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
        
        # Prepare user data for response
        user_list = []
        for user in users:
            user_dict = dict(user)
            # Convert datetime objects to strings for JSON serialization
            user_dict['created_at'] = user_dict['created_at'].isoformat() if user_dict['created_at'] else None
            user_dict['updated_at'] = user_dict['updated_at'].isoformat() if user_dict['updated_at'] else None
            # Remove password for security
            if 'password' in user_dict:
                del user_dict['password']
            user_list.append(user_dict)
        
        # Calculate pagination info
        total_pages = (total_count + limit - 1) // limit
        
        return jsonify({
            'success': True,
            'users': user_list,
            'pagination': {
                'total': total_count,
                'page': page,
            'limit': limit,
                'total_pages': total_pages
            }
        })
    except Exception as e:
        print(f"Error getting users: {e}")
        return jsonify({'success': False, 'error': 'Failed to get users'}), 500

@admin_bp.route('/api/admin/users/<user_id>', methods=['GET'])
@admin_required
def get_user_by_id(user_data, user_id):
    """Get user by ID"""
    try:
        user = User.get_by_id(user_id)
        
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # Convert datetime objects to strings for JSON serialization
        user_dict = dict(user)
        user_dict['created_at'] = user_dict['created_at'].isoformat() if user_dict['created_at'] else None
        user_dict['updated_at'] = user_dict['updated_at'].isoformat() if user_dict['updated_at'] else None
        
        # Remove password for security
        if 'password' in user_dict:
            del user_dict['password']
        
        return jsonify({
            'success': True,
            'user': user_dict
        })
    except Exception as e:
        print(f"Error getting user: {e}")
        return jsonify({'success': False, 'error': 'Failed to get user'}), 500

@admin_bp.route('/api/admin/users', methods=['POST'])
@admin_required
def create_user(user_data):
    """Create a new user"""
    try:
        # Get request data
        data = request.get_json()
        
        # Required fields
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        # Check if username or email already exists
        existing_user = User.get_by_username(data['username'])
        if existing_user:
            return jsonify({'success': False, 'error': 'Username already exists'}), 409
        
        # Create user
        new_user = User.create(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            full_name=data.get('full_name'),
            biography=data.get('biography'),
            is_admin=data.get('is_admin', False),
            avatar=data.get('avatar')
        )
        
        if not new_user:
            return jsonify({'success': False, 'error': 'Failed to create user'}), 500
        
        # Convert datetime objects to strings for JSON serialization
        user_dict = dict(new_user)
        user_dict['created_at'] = user_dict['created_at'].isoformat() if user_dict['created_at'] else None
        user_dict['updated_at'] = user_dict['updated_at'].isoformat() if user_dict['updated_at'] else None
        
        return jsonify({
            'success': True,
            'user': user_dict,
            'message': 'User created successfully'
        }), 201
    except Exception as e:
        print(f"Error creating user: {e}")
        return jsonify({'success': False, 'error': 'Failed to create user'}), 500

@admin_bp.route('/api/admin/users/<user_id>', methods=['PUT'])
@admin_required
def update_user(user_data, user_id):
    """Update user information"""
    try:
        # Get request data
        data = request.get_json()
        
        # Check if user exists
        user = User.get_by_id(user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # Update user information
        updated_user = User.update(
            user_id=user_id,
            username=data.get('username'),
            email=data.get('email'),
            full_name=data.get('full_name'),
            biography=data.get('biography'),
            is_admin=data.get('is_admin'),
            avatar=data.get('avatar')
        )
        
        if not updated_user:
            return jsonify({'success': False, 'error': 'Failed to update user'}), 500
        
        # Update password if provided
        if 'password' in data and data['password']:
            password_updated = User.update_password(user_id, data['password'])
            if not password_updated:
                return jsonify({'success': False, 'error': 'Failed to update password'}), 500
        
        # Convert datetime objects to strings for JSON serialization
        user_dict = dict(updated_user)
        user_dict['created_at'] = user_dict['created_at'].isoformat() if user_dict['created_at'] else None
        user_dict['updated_at'] = user_dict['updated_at'].isoformat() if user_dict['updated_at'] else None
        
        return jsonify({
            'success': True,
            'user': user_dict,
            'message': 'User updated successfully'
        })
    except Exception as e:
        print(f"Error updating user: {e}")
        return jsonify({'success': False, 'error': 'Failed to update user'}), 500

@admin_bp.route('/api/admin/users/<user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_data, user_id):
    """Delete a user"""
    try:
        # Check if user exists
        user = User.get_by_id(user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # Prevent deleting self
        if str(user['id']) == str(user_data['id']):
            return jsonify({'success': False, 'error': 'Cannot delete your own account'}), 403
        
        # Delete user
        success = User.delete(user_id)
        if not success:
            return jsonify({'success': False, 'error': 'Failed to delete user'}), 500
        
        return jsonify({
            'success': True,
            'message': 'User deleted successfully'
        })
    except Exception as e:
        print(f"Error deleting user: {e}")
        return jsonify({'success': False, 'error': 'Failed to delete user'}), 500

@admin_bp.route('/admin/contributions/pending', methods=['GET'])
@admin_bp.route('/api/admin/contributions/pending', methods=['GET'])
@admin_required
def get_pending_contributions(user_data):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute("""
            SELECT c.id as contribution_id, c.status, c.created_at, c.image_id,
                   i.user_caption, i.ai_caption, i.image_path,
                   u.username as contributor
            FROM contributions c
            JOIN images i ON c.image_id = i.image_id
            LEFT JOIN users u ON c.user_id = u.id
            WHERE c.status = 'pending'
            ORDER BY c.created_at ASC
        """)
            
        contributions = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'contributions': contributions,
            'count': len(contributions)
        })
        
    except Exception as e:
        print(f"Error getting pending contributions: {str(e)}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/contribution/<contribution_id>/review', methods=['PUT'])
@admin_required
def review_contribution(user_data, contribution_id):
    """Review a contribution"""
    try:
        # Get request data
        data = request.get_json()
        status = data.get('status')
        review_notes = data.get('notes', '')
        
        # Validate status
        if not status or status not in ['approved', 'rejected']:
            return jsonify({
                'success': False, 
                'error': 'Invalid status value. Must be "approved" or "rejected"'
            }), 400
        
        # Update contribution status
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        try:
            # Update status and add reviewer information
            cursor.execute("""
            UPDATE contributions 
                    SET status = %s, 
                        reviewer_id = %s, 
                        review_notes = %s, 
                        updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
                    RETURNING id, user_id, image_id, status, created_at, updated_at
                """, (status, user_data['id'], review_notes, contribution_id))
            
            contribution = cursor.fetchone()
            
            if not contribution:
                conn.rollback()
                return jsonify({
                    'success': False, 
                    'error': 'Contribution not found'
                }), 404
            
            # Commit the transaction
            conn.commit()
            
            # Convert datetime objects to strings for JSON serialization
            contrib_dict = dict(contribution)
            contrib_dict['created_at'] = contrib_dict['created_at'].isoformat() if contrib_dict['created_at'] else None
            contrib_dict['updated_at'] = contrib_dict['updated_at'].isoformat() if contrib_dict['updated_at'] else None
            
            return jsonify({
                'success': True,
                'contribution': contrib_dict,
                'message': f'Contribution {status} successfully'
            })
        except Exception as e:
            conn.rollback()
            print(f"Error reviewing contribution: {e}")
            return jsonify({
                'success': False,
                'error': f'Database error: {str(e)}'
            }), 500
        finally:
            cursor.close()
            conn.close()
    except Exception as e:
        print(f"Error reviewing contribution: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_bp.route('/admin/dashboard/activity-stats', methods=['GET'])
@admin_bp.route('/api/admin/dashboard/activity-stats', methods=['GET'])
@admin_required
def get_activity_stats(user_data):
    # Get period from query params (default: last 7 days)
    days = int(request.args.get('days', 7))
    if days > 60:  # Maximum 60 days period to avoid performance issues
        days = 60
        
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Get today's date at midnight for consistent comparison
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        # Set end date to be end of current day to include today's data
        end_date = today.replace(hour=23, minute=59, second=59).date()
        # Start date is days-1 days before today
        start_date = (today - timedelta(days=days-1)).date()
        
        print(f"Activity stats date range: {start_date} to {end_date}")
        
        # Generate a series of dates for the x-axis
        date_series = []
        current_date = start_date
        while current_date <= end_date:
            date_series.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)
        
        # Query stats from daily_stats for the period
        cursor.execute("""
            SELECT date, caption_requests, contributions
            FROM daily_stats
            WHERE date >= %s AND date <= %s
            ORDER BY date
        """, (start_date, end_date))
        
        daily_stats = cursor.fetchall()
        
        # Initialize result with zeros for all days
        caption_requests_data = {date: 0 for date in date_series}
        contributions_data = {date: 0 for date in date_series}
        
        # Fill in the actual data
        for stat in daily_stats:
            date_str = stat['date'].strftime('%Y-%m-%d')
            if date_str in caption_requests_data:
                caption_requests_data[date_str] = stat['caption_requests'] or 0
                contributions_data[date_str] = stat['contributions'] or 0
        
        # Format for chart display
        formatted_dates = []
        caption_requests_series = []
        contributions_series = []
        
        for date_str in date_series:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            formatted_date = date_obj.strftime('%d/%m')  # Standard format with leading zeros
            formatted_dates.append(formatted_date)
            caption_requests_series.append(caption_requests_data[date_str])
            contributions_series.append(contributions_data[date_str])
        
        # Calculate summary statistics
        cursor.execute("""
            SELECT 
                SUM(caption_requests) as total_captions,
                SUM(contributions) as total_contributions,
                SUM(ratings) as total_ratings,
                AVG(average_rating) as average_rating
            FROM daily_stats
            WHERE date >= %s AND date <= %s
        """, (start_date, end_date))
        
        summary = cursor.fetchone()
        
        # Handle None values
        if not summary['total_captions']:
            summary['total_captions'] = 0
        if not summary['total_contributions']:
            summary['total_contributions'] = 0
        if not summary['total_ratings']:
            summary['total_ratings'] = 0
        if not summary['average_rating']:
            summary['average_rating'] = 0
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'categories': formatted_dates,
            'series': [
                {
                    'name': 'Tạo caption',  # Changed to match dashboard stats naming
                    'data': caption_requests_series
                },
                {
                    'name': 'Đóng góp ảnh',  # Changed to match dashboard stats naming
                    'data': contributions_series
                }
            ],
            'summary': summary,
            'period': {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'days': days
            }
        })
    except Exception as e:
        print(f"Error getting activity stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_bp.route('/admin/contributions', methods=['GET'])
@admin_bp.route('/api/admin/contributions', methods=['GET'])
@admin_required
def get_all_contributions(user_data):
    """Get all contributions with pagination, search, and status filtering"""
    try:
        # Parse query parameters
        page = int(request.args.get('page', 1))
        limit = min(int(request.args.get('limit', 20)), 100)  # Cap at 100
        status = request.args.get('status')
        search = request.args.get('search', '')
        offset = (page - 1) * limit
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Build the base query
        query = """
            SELECT c.id as contribution_id, c.status, c.review_notes, 
                   c.created_at, c.updated_at,
                   i.image_id, i.user_caption, i.ai_caption, i.image_path,
                   u.username as contributor, u.id as user_id,
                   r.username as reviewer_name, r.id as reviewer_id
            FROM contributions c
            JOIN images i ON c.image_id = i.image_id
            LEFT JOIN users u ON c.user_id = u.id
            LEFT JOIN users r ON c.reviewer_id = r.id
            WHERE 1=1
        """
        
        # Build count query
        count_query = """
            SELECT COUNT(*) as total
            FROM contributions c
            JOIN images i ON c.image_id = i.image_id
            LEFT JOIN users u ON c.user_id = u.id
            WHERE 1=1
        """
        
        # Add filters
        params = []
        
        # Filter by status if provided
        if status:
            query += " AND c.status = %s"
            count_query += " AND c.status = %s"
            params.append(status)
        
        # Add search if provided
        if search:
            search_term = f"%{search}%"
            query += " AND (i.user_caption ILIKE %s OR i.ai_caption ILIKE %s OR u.username ILIKE %s)"
            count_query += " AND (i.user_caption ILIKE %s OR i.ai_caption ILIKE %s OR u.username ILIKE %s)"
            params.extend([search_term, search_term, search_term])
        
        # Add ordering
        query += " ORDER BY c.created_at DESC"
        
        # Add pagination
        query += " LIMIT %s OFFSET %s"
        pagination_params = params.copy()
        pagination_params.extend([limit, offset])
        
        # Execute count query to get total
        cursor.execute(count_query, params)
        total_result = cursor.fetchone()
        total = total_result['total'] if total_result else 0
        
        # Execute main query with pagination
        cursor.execute(query, pagination_params)
        contributions = cursor.fetchall()
        
        # Convert datetime objects to strings for JSON serialization
        for contrib in contributions:
            if contrib.get('created_at'):
                contrib['created_at'] = contrib['created_at'].isoformat()
            if contrib.get('updated_at'):
                contrib['updated_at'] = contrib['updated_at'].isoformat()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'contributions': contributions,
            'total': total,
            'page': page,
            'limit': limit,
            'pages': (total + limit - 1) // limit  # Ceiling division
        })
        
    except Exception as e:
        print(f"Error getting contributions: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/admin/contributions/<contribution_id>', methods=['PUT'])
@admin_required
def update_contribution_by_id(user_data, contribution_id):
    """Update a contribution by its contribution_id"""
    try:
        # Get request data
        data = request.get_json()
        user_caption = data.get('user_caption')
        ai_caption = data.get('ai_caption')
        status = data.get('status')
        review_notes = data.get('review_notes', '')
        
        # Connect to DB
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        try:
            # First, get the contribution and related image_id
            cursor.execute("""
                SELECT c.id, c.image_id, c.user_id, c.status 
                FROM contributions c
                WHERE c.id = %s
            """, (contribution_id,))
            
            contribution = cursor.fetchone()
            
            if not contribution:
                conn.rollback()
                return jsonify({'success': False, 'error': 'Contribution not found'}), 404
            
            # Update the image captions if provided
            image_id = contribution['image_id']
            update_queries = []
            
            if user_caption is not None:
                cursor.execute("""
                    UPDATE images 
                    SET user_caption = %s
                    WHERE image_id = %s
                """, (user_caption, image_id))
            
            if ai_caption is not None:
                cursor.execute("""
                    UPDATE images 
                    SET ai_caption = %s
                    WHERE image_id = %s
                """, (ai_caption, image_id))
            
            # Update contribution status if provided
            if status is not None:
                cursor.execute("""
                    UPDATE contributions 
                    SET status = %s, 
                        reviewer_id = %s, 
                        review_notes = %s, 
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (status, user_data['id'], review_notes, contribution_id))
            
            # Commit the transaction
            conn.commit()
            
            return jsonify({
                'success': True,
                'message': 'Contribution updated successfully'
            })
        except Exception as e:
            conn.rollback()
            print(f"Error updating contribution: {e}")
            return jsonify({'success': False, 'error': f'Database error: {str(e)}'}), 500
        finally:
            cursor.close()
            conn.close()
    except Exception as e:
        print(f"Error updating contribution: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/admin/contributions/<contribution_id>', methods=['DELETE'])
@admin_required
def delete_contribution_by_id(user_data, contribution_id):
    """Delete a contribution by its contribution_id"""
    try:
        # Connect to DB
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # First, get the contribution and related image info
            cursor.execute("""
                SELECT c.id, c.image_id, i.image_path 
                FROM contributions c
                JOIN images i ON c.image_id = i.image_id
                WHERE c.id = %s
            """, (contribution_id,))
            
            result = cursor.fetchone()
            
            if not result:
                conn.rollback()
                return jsonify({'success': False, 'error': 'Contribution not found'}), 404
            
            image_id = result[1]
            image_path = result[2]
            
            # Delete the contribution
            cursor.execute("DELETE FROM contributions WHERE id = %s", (contribution_id,))
            
            # Delete the image
            cursor.execute("DELETE FROM images WHERE image_id = %s", (image_id,))
            
            # Commit the transaction
            conn.commit()
            
            # Delete the physical file
            full_path = os.path.join(UPLOAD_FOLDER, image_path)
            if os.path.exists(full_path):
                os.remove(full_path)
            
            return jsonify({
                'success': True,
                'message': 'Contribution deleted successfully'
            })
        except Exception as e:
            conn.rollback()
            print(f"Error deleting contribution: {e}")
            return jsonify({'success': False, 'error': f'Database error: {str(e)}'}), 500
        finally:
            cursor.close()
            conn.close()
    except Exception as e:
        print(f"Error deleting contribution: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/admin/dashboard/stats', methods=['GET'])
@admin_bp.route('/api/admin/dashboard/stats', methods=['GET'])
@admin_required
def get_dashboard_stats(user_data):
    """Get basic statistics for the dashboard."""
    try:
        print("Get dashboard stats API called")
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Get total number of captions
        cursor.execute("""
            SELECT COUNT(*) AS total_captions 
            FROM images 
            WHERE ai_caption IS NOT NULL
        """)
        total_captions = cursor.fetchone()['total_captions']
        print(f"Total captions: {total_captions}")
        
        # Get total number of contributed images
        cursor.execute("""
            SELECT COUNT(*) AS total_contributions 
            FROM contributions
        """)
        total_contributions = cursor.fetchone()['total_contributions']
        print(f"Total contributions: {total_contributions}")
        
        # Get total number of ratings
        cursor.execute("""
            SELECT COUNT(*) AS total_ratings 
            FROM caption_ratings
        """)
        total_ratings = cursor.fetchone()['total_ratings']
        print(f"Total ratings: {total_ratings}")
        
        # Get average rating
        cursor.execute("""
            SELECT COALESCE(AVG(rating), 0) AS average_rating 
            FROM caption_ratings
        """)
        average_rating = cursor.fetchone()['average_rating']
        print(f"Average rating: {average_rating}")
        
        # Get previous activity data for the chart
        days = int(request.args.get('days', 7))
        print(f"Requested days: {days}")
        
        # Get today's date at midnight for consistent comparison
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        # Set end date to be end of current day to include today's data
        end_date = today.replace(hour=23, minute=59, second=59)
        # Start date is days-1 days before today
        start_date = today - timedelta(days=days-1)
        
        print(f"Date range: {start_date} to {end_date}")
        
        # Get caption and contribution counts per day
        cursor.execute("""
            WITH dates AS (
                SELECT date_trunc('day', generate_series(
                    %s::timestamp,
                    %s::timestamp,
                    '1 day'
                )) AS day
            ),
            captions AS (
                SELECT date_trunc('day', created_at) AS day, COUNT(*) AS count
                FROM images
                WHERE created_at >= %s AND created_at <= %s AND ai_caption IS NOT NULL
                GROUP BY day
            ),
            contributions AS (
                SELECT date_trunc('day', created_at) AS day, COUNT(*) AS count
                FROM contributions
                WHERE created_at >= %s AND created_at <= %s
                GROUP BY day
            )
            SELECT 
                to_char(d.day, 'YYYY-MM-DD') AS date,
                COALESCE(c.count, 0) AS caption_count,
                COALESCE(cont.count, 0) AS contribution_count
            FROM dates d
            LEFT JOIN captions c ON d.day = c.day
            LEFT JOIN contributions cont ON d.day = cont.day
            ORDER BY d.day
        """, (start_date, end_date, start_date, end_date, start_date, end_date))
        
        daily_stats = cursor.fetchall()
        print(f"Daily stats results: {len(daily_stats)} rows")
        
        # Format data for chart
        categories = []
        caption_series = []
        contribution_series = []
        
        if daily_stats:
            for stat in daily_stats:
                # Format date to be DD/MM
                date_obj = datetime.strptime(stat['date'], '%Y-%m-%d')
                formatted_date = date_obj.strftime('%d/%m')  # Use standard format without %-d which might not be supported in all systems
                
                categories.append(formatted_date)
                caption_count = stat['caption_count']
                contribution_count = stat['contribution_count']
                caption_series.append(caption_count)
                contribution_series.append(contribution_count)
                print(f"Date: {formatted_date}, Captions: {caption_count}, Contributions: {contribution_count}")
        else:
            print("No daily stats data found, using empty arrays with zero values")
            # If no data found, still create a date range with zeros
            for i in range(days):
                day = today - timedelta(days=days-i-1)
                formatted_date = day.strftime('%d/%m')  # Standard format with leading zeros
                categories.append(formatted_date)
                caption_series.append(0)
                contribution_series.append(0)
                
        cursor.close()
        conn.close()
        
        # Response data
        data = {
            'totalCaptions': total_captions or 0,
            'totalContributions': total_contributions or 0,
            'totalRatings': total_ratings or 0,
            'averageRating': float(average_rating) or 0.0,
            'series': [
                {'name': 'Tạo caption', 'data': caption_series},
                {'name': 'Đóng góp ảnh', 'data': contribution_series}
            ],
            'categories': categories,
            'summary': {
                'total_captions': total_captions or 0,
                'total_contributions': total_contributions or 0
            }
        }
        
        print("Dashboard stats data prepared successfully")
        print(f"Series data: {data['series']}")
        print(f"Categories: {data['categories']}")
        
        return jsonify({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        print(f"Error getting dashboard stats: {str(e)}")
        # Return empty data with proper structure in case of error
        # No mock data, just zeros
        categories = []
        caption_series = []
        contribution_series = []
        
        # Create date range with zeros - today and previous (days-1) days
        days = int(request.args.get('days', 7))
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        for i in range(days):
            day = today - timedelta(days=days-i-1)
            formatted_date = day.strftime('%d/%m')  # Standard format with leading zeros
            categories.append(formatted_date)
            caption_series.append(0)
            contribution_series.append(0)
        
        return jsonify({
            'success': True,
            'data': {
                'totalCaptions': 0,
                'totalContributions': 0,
                'totalRatings': 0,
                'averageRating': 0.0,
                'series': [
                    {'name': 'Tạo caption', 'data': caption_series},
                    {'name': 'Đóng góp ảnh', 'data': contribution_series}
                ],
                'categories': categories,
                'summary': {
                    'total_captions': 0,
                    'total_contributions': 0
                }
            }
        })

@admin_bp.route('/admin/top-contributors', methods=['GET'])
@admin_bp.route('/api/admin/top-contributors', methods=['GET'])
@admin_required
def get_top_contributors(user_data):
    """Get top contributors based on the number of contributions."""
    try:
        # Get requested limit (default: 5, max: 10)
        limit = min(int(request.args.get('limit', 5)), 10)
        
        print(f"Getting top {limit} contributors")
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Query to get the top contributors based on contribution count
        cursor.execute("""
            WITH user_contrib_counts AS (
                SELECT 
                    u.id,
                    u.username,
                    COUNT(c.id) AS contribution_count,
                    MAX(c.created_at) AS last_contribution_date
                FROM users u
                JOIN contributions c ON u.id = c.user_id
                GROUP BY u.id, u.username
                ORDER BY contribution_count DESC, last_contribution_date DESC
                LIMIT %s
            )
            SELECT 
                id,
                username,
                contribution_count,
                to_char(last_contribution_date, 'DD/MM/YYYY') AS last_contribution
            FROM user_contrib_counts
        """, (limit,))
        
        contributors = cursor.fetchall()
        print(f"Found {len(contributors)} top contributors")
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': contributors
        })
        
    except Exception as e:
        print(f"Error getting top contributors: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_bp.route('/api/admin/contributions/count', methods=['GET'])
@admin_required
def count_contributions_by_status(user_data):
    """
    Count contributions by status.
    Query parameter: status (optional) - Filter by status (approved, rejected, pending)
    """
    try:
        status = request.args.get('status')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "SELECT COUNT(*) FROM contributions"
        params = []
        
        if status:
            query += " WHERE status = %s"
            params.append(status)
            
        cursor.execute(query, params)
        count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'count': count
        })
        
    except Exception as e:
        print(f"Error counting contributions: {str(e)}")
        return jsonify({'error': str(e), 'success': False}), 500

@admin_bp.route('/api/admin/download/generate', methods=['POST'])
@admin_required
def generate_download_package(user_data):
    """
    Generate a zip file containing all approved images and a JSON file with captions.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Get all approved contributions with their captions and storage info
        cursor.execute("""
            SELECT c.id, i.image_path, i.user_caption, i.ai_caption, c.created_at, i.storage_type
            FROM contributions c
            JOIN images i ON c.image_id = i.image_id
            WHERE c.status = 'approved'
            ORDER BY c.created_at
        """)
        
        approved_contributions = cursor.fetchall()
        
        if not approved_contributions:
            return jsonify({'error': 'No approved contributions found', 'success': False}), 404
        
        # Create a memory file for the zip
        memory_file = io.BytesIO()
        
        # Track statistics
        total_approved = len(approved_contributions)
        images_included = 0
        missing_files = []
        
        # Create the zip file
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Prepare JSON data - include ALL approved captions
            captions_data = {}
            
            for contribution in approved_contributions:
                image_filename = os.path.basename(contribution['image_path'])
                storage_type = contribution.get('storage_type', 'local')
                
                # Always add caption to JSON data
                captions_data[image_filename] = {
                    "id": str(contribution['id']),
                    "user_caption": contribution['user_caption'] or "",
                    "ai_caption": contribution['ai_caption'] or "",
                    "created_at": contribution['created_at'].isoformat() if contribution['created_at'] else None,
                    "image_path": contribution['image_path'],
                    "storage_type": storage_type
                }
                
                # Try to add image to zip based on storage type
                try:
                    if storage_type == 'gcs' and GCS_ENABLED:
                        # Download from Google Cloud Storage
                        print(f"Downloading image from GCS: {contribution['image_path']}")
                        image_data = download_image(contribution['image_path'])
                        zf.writestr(f"images/{image_filename}", image_data)
                        images_included += 1
                        captions_data[image_filename]["file_included"] = True
                        print(f"Added GCS image to zip: {image_filename}")
                    else:
                        # Local storage
                        image_path = os.path.join(UPLOAD_FOLDER, contribution['image_path'])
                        if os.path.exists(image_path):
                            zf.write(image_path, f"images/{image_filename}")
                            images_included += 1
                            captions_data[image_filename]["file_included"] = True
                            print(f"Added local image to zip: {image_filename}")
                        else:
                            print(f"Local image file not found: {image_path}")
                            captions_data[image_filename]["file_included"] = False
                            captions_data[image_filename]["error"] = "Local file not found on server"
                            missing_files.append(f"{image_filename} (local file not found)")
                except Exception as e:
                    print(f"Error adding image {image_filename} to zip: {str(e)}")
                    captions_data[image_filename]["file_included"] = False
                    captions_data[image_filename]["error"] = str(e)
                    missing_files.append(f"{image_filename} (error: {str(e)})")
                    
            # Write captions JSON to zip
            captions_json = json.dumps(captions_data, indent=2, ensure_ascii=False)
            zf.writestr("captions.json", captions_json)
            
            # Create summary report
            summary_report = f"""# Báo Cáo Tải Xuống Dữ Liệu

## Thống kê
- Tổng số đóng góp đã duyệt: {total_approved}
- Số ảnh có trong gói: {images_included}
- Số ảnh bị thiếu: {len(missing_files)}
- Ngày tạo: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Danh sách ảnh bị thiếu
"""
            if missing_files:
                for missing in missing_files:
                    summary_report += f"- {missing}\n"
            else:
                summary_report += "- Không có ảnh nào bị thiếu\n"
                
            summary_report += f"""
## Cấu trúc gói dữ liệu
- `/images/`: Thư mục chứa {images_included} hình ảnh đã được chấp nhận
- `/captions.json`: File JSON chứa mô tả cho tất cả {total_approved} đóng góp (bao gồm cả ảnh bị thiếu)
- `/download_report.txt`: Báo cáo này

## Định dạng JSON
```
{{
  "image_filename.jpg": {{
    "id": "ID của đóng góp",
    "user_caption": "Mô tả do người dùng cung cấp",
    "ai_caption": "Mô tả AI (tham khảo)",
    "created_at": "Thời gian tạo",
    "image_path": "Đường dẫn ảnh gốc",
    "file_included": true/false,
    "error": "Lỗi nếu có"
  }},
  ...
}}
```

Được tạo tự động bởi Hệ Thống Chú Thích Hình Ảnh.
"""
            zf.writestr("download_report.txt", summary_report)
        
        cursor.close()
        conn.close()
        
        # Reset file pointer to start
        memory_file.seek(0)
        
        # Create activity log with detailed stats
        track_activity("download_approved_data", user_data.get('id'), {
            "total_approved": total_approved,
            "images_included": images_included,
            "missing_files": len(missing_files),
            "timestamp": datetime.now().isoformat()
        })
        
        print(f"Download package generated: {images_included}/{total_approved} images included")
        
        # Return the zip file
        return memory_file.getvalue(), 200, {
            'Content-Type': 'application/zip',
            'Content-Disposition': f'attachment; filename=approved-images-{datetime.now().strftime("%Y-%m-%d")}.zip'
        }
        
    except Exception as e:
        print(f"Error generating download package: {str(e)}")
        return jsonify({'error': str(e), 'success': False}), 500

@admin_bp.route('/api/admin/caption/<image_id>', methods=['DELETE'])
@admin_required
def delete_caption_by_id(user_data, image_id):
    """Delete a caption/image from history by its image_id"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if image exists
        cursor.execute("SELECT id FROM images WHERE image_id = %s", (image_id,))
        image = cursor.fetchone()
        
        if not image:
            cursor.close()
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Image not found'
            }), 404
        
        # Delete related records in caption_ratings
        cursor.execute("DELETE FROM caption_ratings WHERE image_id = %s", (image_id,))
        
        # Delete image record
        cursor.execute("DELETE FROM images WHERE image_id = %s RETURNING image_path, storage_type", (image_id,))
        deleted_image = cursor.fetchone()
        
        # Commit the transaction
        conn.commit()
        
        if deleted_image:
            image_path, storage_type = deleted_image
            
            # Track this activity
            admin_id = user_data.get('id')
            track_activity(
                activity_type='delete_caption',
                user_id=admin_id,
                details={
                    'image_id': image_id,
                    'admin_id': admin_id
                }
            )
            
            # Could also delete the actual file here if needed
            # That would be implemented in a future update
            
            return jsonify({
                'success': True,
                'message': 'Caption deleted successfully',
                'image_id': image_id
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to delete caption'
            }), 500
            
    except Exception as e:
        print(f"Error deleting caption: {str(e)}")
        
        # Rollback in case of error
        if conn:
            conn.rollback()
            
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
