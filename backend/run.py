from app import create_app
from app.utils.db import initialize_database
from app.services.model_service import load_model
import sys
import os
from flask import Flask

app = create_app()

if __name__ == '__main__':
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")

    # Check for flask_cors
    try:
        from flask_cors import CORS
        print("Flask-CORS is installed correctly")
    except ImportError:
        print("WARNING: Flask-CORS is not installed! Install with: pip install flask-cors")

    # Initialize database
    with app.app_context():
        print("Initializing database...")
        initialize_database()
        print("Database initialization complete.")

    # Load model
    print("Loading model...")
    load_model()
    print("Model loading complete.")

    # Run the app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

