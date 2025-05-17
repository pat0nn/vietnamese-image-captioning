import os
import psycopg2
import psycopg2.extras
from psycopg2.extras import RealDictCursor
from app.config.settings import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

def get_db_connection():
    """Get a connection to the database"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        conn.autocommit = True
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        raise

def initialize_database():
    """Initialize the database with required tables"""
    conn = None
    try:
        # Create a connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if storage_type column exists in images table
        cursor.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'images' AND column_name = 'storage_type'
        """)
        storage_type_exists = cursor.fetchone() is not None
        
        # Create users table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                full_name VARCHAR(100),
                biography TEXT,
                position VARCHAR(100),
                country VARCHAR(50),
                is_admin BOOLEAN DEFAULT FALSE,
                status VARCHAR(20) DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                avatar VARCHAR(255)
            )
        """)
        
        # Create images table if it doesn't exist
        if not storage_type_exists:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS images (
                    id SERIAL PRIMARY KEY,
                    image_id VARCHAR(100) UNIQUE NOT NULL,
                    image_path VARCHAR(255) NOT NULL,
                    user_caption TEXT,
                    ai_caption TEXT,
                    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                    is_flagged BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    storage_type VARCHAR(10) DEFAULT 'local'
                )
            """)
        else:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS images (
                    id SERIAL PRIMARY KEY,
                    image_id VARCHAR(100) UNIQUE NOT NULL,
                    image_path VARCHAR(255) NOT NULL,
                    user_caption TEXT,
                    ai_caption TEXT,
                    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                    is_flagged BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        
        # Create contributions table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contributions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                image_id VARCHAR(100) NOT NULL,
                status VARCHAR(20) DEFAULT 'pending',
                reviewer_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                review_notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create caption_ratings table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS caption_ratings (
                id SERIAL PRIMARY KEY,
                image_id VARCHAR(100) NOT NULL,
                user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create user_activities table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_activities (
                id SERIAL PRIMARY KEY,
                activity_type VARCHAR(50) NOT NULL,
                user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                ip_address VARCHAR(50),
                details JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create model_versions table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS model_versions (
                id SERIAL PRIMARY KEY,
                version_name VARCHAR(100) NOT NULL,
                model_path VARCHAR(255) NOT NULL,
                is_active BOOLEAN DEFAULT FALSE,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create daily_stats table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_stats (
                id SERIAL PRIMARY KEY,
                date DATE UNIQUE NOT NULL,
                caption_requests INTEGER DEFAULT 0,
                contributions INTEGER DEFAULT 0,
                ratings INTEGER DEFAULT 0,
                ratings_sum INTEGER DEFAULT 0,
                visits INTEGER DEFAULT 0,
                average_rating NUMERIC(3,2) DEFAULT 0.00,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create a default admin user if no users exist
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        if user_count == 0:
            # Import bcrypt only when needed to avoid circular imports
            import bcrypt
            hashed_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            cursor.execute("""
                INSERT INTO users (username, email, password, full_name, is_admin)
                VALUES (%s, %s, %s, %s, %s)
            """, ('admin', 'admin@example.com', hashed_password, 'Administrator', True))
            
            print("Default admin user created: username='admin', password='admin123'")
        
        # Add storage_type column to tables if it doesn't exist
        if not storage_type_exists:
            cursor.execute('''
                ALTER TABLE images 
                ADD COLUMN storage_type VARCHAR(10) DEFAULT 'local'
            ''')
            print("Added storage_type column to images table")
        
        cursor.close()
        conn.close()
        
        print("Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise

def execute_query(query, params=None, fetch_one=False, dict_cursor=True):
    """Execute a database query and return the results"""
    try:
        conn = get_db_connection()
        
        # Use RealDictCursor to get results as dictionaries if requested
        if dict_cursor:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
        else:
            cursor = conn.cursor()
        
        cursor.execute(query, params or ())
        
        if query.strip().upper().startswith(('SELECT', 'WITH')):
            if fetch_one:
                result = cursor.fetchone()
            else:
                result = cursor.fetchall()
        else:
            if 'RETURNING' in query.upper():
                if fetch_one:
                    result = cursor.fetchone()
                else:
                    result = cursor.fetchall()
            else:
                result = cursor.rowcount
        
        cursor.close()
        conn.close()
        
        return result
    except Exception as e:
        print(f"Database query error: {e}")
        raise
