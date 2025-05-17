from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
import os
import logging
from app.utils.db import initialize_database
from app.routes.auth_routes import auth_bp
from app.routes.admin_routes import admin_bp
from app.routes.image_routes import image_bp
from app.routes.tts_routes import tts_bp
from app.routes.frontend_routes import frontend_bp
from app.routes.avatar_routes import avatar_bp
from app.config.settings import ALLOWED_ORIGINS

def create_app(test_config=None):
    # Cấu hình logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    # Configure CORS with Flask-CORS - this is the only CORS configuration we'll use
    CORS(app, 
         supports_credentials=True, 
         origins=ALLOWED_ORIGINS,
         allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
         expose_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )
    
    # Handle OPTIONS request for preflight requests
    @app.route('/', methods=['OPTIONS'])
    @app.route('/<path:path>', methods=['OPTIONS'])
    def options_handler(path=None):
        pass
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(image_bp)
    app.register_blueprint(tts_bp)
    app.register_blueprint(frontend_bp)
    app.register_blueprint(avatar_bp)
    
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Initialize database
    with app.app_context():
        initialize_database()
    
    # Pre-load model
    try:
        from app.services.model_service import load_model
        load_model()
        logging.info("Model pre-loaded successfully")
    except Exception as e:
        logging.error(f"Error pre-loading model: {str(e)}")
    
    # Simple route to verify server is running
    @app.route('/')
    def hello():
        return {
            'status': 'success',
            'message': 'Vietnamese Image Captioning API is running!'
        }
    
    return app