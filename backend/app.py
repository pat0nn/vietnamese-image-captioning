from flask import Flask, request, jsonify
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

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

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
        
        # Create images table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS images (
                id SERIAL PRIMARY KEY,
                image_id VARCHAR(50) UNIQUE NOT NULL,
                image_path VARCHAR(255) NOT NULL,
                user_caption TEXT,
                ai_caption TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.close()
        conn.close()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {str(e)}")

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

# API route for image captioning
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

# API route to save user contributed data
@app.route('/api/contribute', methods=['POST'])
def contribute_data():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    
    file = request.files['image']
    user_caption = request.form.get('userCaption', '')
    
    try:
        # Read and convert image
        image_bytes = file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        
        # Generate AI caption
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
        image_path = os.path.join(UPLOAD_FOLDER, f"{image_id}.jpg")
        image.save(image_path)
        
        # Save to database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            INSERT INTO images (image_id, image_path, user_caption, ai_caption)
            VALUES (%s, %s, %s, %s)
            RETURNING id
            """,
            (image_id, image_path, user_caption, ai_caption)
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

# API to get all contributed images
@app.route('/api/contributions', methods=['GET'])
def get_contributions():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("SELECT * FROM images ORDER BY created_at DESC")
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

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000) 