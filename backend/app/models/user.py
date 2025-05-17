import psycopg2
import psycopg2.extras
import bcrypt
import uuid
from datetime import datetime
from app.utils.db import get_db_connection

class User:
    def __init__(self, id=None, username=None, email=None, password=None, full_name=None,
                 biography=None, is_admin=False, 
                 created_at=None, updated_at=None, avatar=None):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.full_name = full_name
        self.biography = biography
        self.is_admin = is_admin
        self.created_at = created_at
        self.updated_at = updated_at
        self.avatar = avatar or 'default.jpg'

    @staticmethod
    def create_table():
        """Create users table if it doesn't exist"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    full_name VARCHAR(255),
                    biography TEXT,
                    is_admin BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    avatar VARCHAR(255) DEFAULT 'default.jpg'
                )
            """)
            conn.commit()
            print("Users table created successfully")
        except Exception as e:
            conn.rollback()
            print(f"Error creating users table: {e}")
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def get_all():
        """Get all users"""
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        try:
            cursor.execute("""
                SELECT id, username, email, full_name, biography,
                    is_admin, created_at, updated_at, avatar
                FROM users
                ORDER BY created_at DESC
            """)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error fetching users: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def get_by_id(user_id):
        """Get user by ID"""
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        try:
            cursor.execute("""
                SELECT id, username, email, full_name, biography,
                    is_admin, created_at, updated_at, avatar
                FROM users 
                WHERE id = %s
            """, (user_id,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Error fetching user by ID: {e}")
            return None
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def get_by_username(username):
        """Get user by username"""
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        try:
            cursor.execute("""
                SELECT * FROM users WHERE username = %s
            """, (username,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Error fetching user by username: {e}")
            return None
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def create(username, email, password, full_name=None, biography=None, 
               is_admin=False, avatar=None):
        """Create a new user"""
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        try:
            # Hash the password
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            cursor.execute("""
                INSERT INTO users (username, email, password, full_name, biography, 
                                  is_admin, avatar)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id, username, email, full_name, biography,
                         is_admin, created_at, updated_at, avatar
            """, (username, email, hashed_password, full_name, biography, 
                 is_admin, avatar or 'default.jpg'))
            
            new_user = cursor.fetchone()
            conn.commit()
            return new_user
        except Exception as e:
            conn.rollback()
            print(f"Error creating user: {e}")
            return None
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def update(user_id, username=None, email=None, full_name=None, biography=None, 
               is_admin=None, avatar=None):
        """Update user information"""
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        try:
            # Build the dynamic update query
            update_fields = []
            params = []
            
            if username is not None:
                update_fields.append("username = %s")
                params.append(username)
            
            if email is not None:
                update_fields.append("email = %s")
                params.append(email)
            
            if full_name is not None:
                update_fields.append("full_name = %s")
                params.append(full_name)
            
            if biography is not None:
                update_fields.append("biography = %s")
                params.append(biography)
            
            if is_admin is not None:
                update_fields.append("is_admin = %s")
                params.append(is_admin)
            
            if avatar is not None:
                update_fields.append("avatar = %s")
                params.append(avatar)
            
            # Add updated_at timestamp
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            
            # If no fields to update
            if not update_fields:
                return None
            
            # Construct the SQL query
            query = f"""
                UPDATE users 
                SET {', '.join(update_fields)}
                WHERE id = %s
                RETURNING id, username, email, full_name, biography,
                         is_admin, created_at, updated_at, avatar
            """
            
            # Add the user_id to parameters
            params.append(user_id)
            
            cursor.execute(query, params)
            updated_user = cursor.fetchone()
            conn.commit()
            return updated_user
        except Exception as e:
            conn.rollback()
            print(f"Error updating user: {e}")
            return None
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def update_password(user_id, new_password):
        """Update user password"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Hash the new password
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            cursor.execute("""
                UPDATE users 
                SET password = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING id
            """, (hashed_password, user_id))
            
            result = cursor.fetchone()
            conn.commit()
            return result is not None
        except Exception as e:
            conn.rollback()
            print(f"Error updating password: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def delete(user_id):
        """Delete a user"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM users WHERE id = %s RETURNING id", (user_id,))
            result = cursor.fetchone()
            conn.commit()
            return result is not None
        except Exception as e:
            conn.rollback()
            print(f"Error deleting user: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def verify_password(stored_password, provided_password):
        """Verify a user's password against stored hash"""
        try:
            print(f"Verifying password: stored={type(stored_password).__name__}, provided={type(provided_password).__name__}")
            
            # Ensure the stored password is properly encoded
            if isinstance(stored_password, str):
                stored_password = stored_password.encode('utf-8')
                print("Converted stored password from string to bytes")
            
            # Ensure the provided password is properly encoded
            if isinstance(provided_password, str):
                provided_password = provided_password.encode('utf-8')
                print("Converted provided password from string to bytes")
            
            # Log the values for debugging (partial to avoid logging the actual password)
            print(f"Stored password (first 10 bytes): {stored_password[:10]}")
            print(f"Provided password encoded (first 10 bytes): {provided_password[:10]}")
            
            # Compare the password with the hash
            result = bcrypt.checkpw(provided_password, stored_password)
            print(f"Password verification result: {result}")
            return result
        except Exception as e:
            print(f"Password verification error: {str(e)}")
            print(f"Stored password type: {type(stored_password)}")
            print(f"Provided password type: {type(provided_password)}")
            return False
    
    @staticmethod
    def search(query, limit=20, offset=0):
        """Search for users by username, email, or full_name"""
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        try:
            search_pattern = f"%{query}%"
            cursor.execute("""
                SELECT id, username, email, full_name, biography,
                    is_admin, created_at, updated_at, avatar
                FROM users
                WHERE username ILIKE %s OR email ILIKE %s OR full_name ILIKE %s
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """, (search_pattern, search_pattern, search_pattern, limit, offset))
            
            users = cursor.fetchall()
            
            # Get total count for pagination
            cursor.execute("""
                SELECT COUNT(*) FROM users
                WHERE username ILIKE %s OR email ILIKE %s OR full_name ILIKE %s
            """, (search_pattern, search_pattern, search_pattern))
            
            total_count = cursor.fetchone()[0]
            
            return users, total_count
        except Exception as e:
            print(f"Error searching users: {e}")
            return [], 0
        finally:
            cursor.close()
            conn.close() 