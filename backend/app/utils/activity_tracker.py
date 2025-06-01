import json
from datetime import datetime
from app.utils.db import get_db_connection

def track_activity(activity_type, user_id, details=None):
    """
    Track user activity in the database
    
    Parameters:
    - activity_type (str): Type of activity (caption, contribution, review, etc)
    - user_id (int): ID of the user performing the activity
    - details (dict, optional): Additional details about the activity
    
    Returns:
    - bool: True if successfully tracked, False otherwise
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Convert details to JSON string if provided
        details_json = None
        if details:
            details_json = json.dumps(details)
        
        # Insert activity record
        cursor.execute("""
            INSERT INTO user_activities 
            (user_id, activity_type, details, created_at)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (user_id, activity_type, details_json, datetime.now()))
        
        activity_id = cursor.fetchone()[0]
        
        # Update daily stats counter for this activity type
        today = datetime.now().date()
        
        # Try to update existing stats for today
        if activity_type == 'caption':
            cursor.execute("""
                UPDATE daily_stats 
                SET caption_requests = caption_requests + 1
                WHERE date = %s
            """, (today,))
        elif activity_type == 'contribution':
            cursor.execute("""
                UPDATE daily_stats 
                SET contributions = contributions + 1
                WHERE date = %s
            """, (today,))
        elif activity_type == 'rating':
            # For ratings, we need to update both count and average
            if details and 'rating' in details:
                rating = float(details['rating'])
                cursor.execute("""
                    UPDATE daily_stats 
                    SET ratings = ratings + 1,
                        average_rating = (average_rating * ratings + %s) / (ratings + 1)
                    WHERE date = %s
                """, (rating, today))
        
        # If no rows were updated (no stats for today yet), create a new record
        if cursor.rowcount == 0:
            # Default values
            caption_requests = 1 if activity_type == 'caption' else 0
            contributions = 1 if activity_type == 'contribution' else 0
            ratings = 1 if activity_type == 'rating' else 0
            average_rating = float(details['rating']) if activity_type == 'rating' and details and 'rating' in details else 0
            
            cursor.execute("""
                INSERT INTO daily_stats 
                (date, caption_requests, contributions, ratings, average_rating)
                VALUES (%s, %s, %s, %s, %s)
            """, (today, caption_requests, contributions, ratings, average_rating))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True
    except Exception as e:
        print(f"Error tracking activity: {str(e)}")
        return False 