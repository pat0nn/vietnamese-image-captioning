from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import json

app = Flask(__name__)

# Cấu hình CORS test
ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'https://icy-river-037493600.6.azurestaticapps.net'
]

# Cấu hình CORS không dùng credentials
CORS(app, resources={r"/*": {"origins": ALLOWED_ORIGINS}})

@app.route('/api/test', methods=['GET', 'OPTIONS'])
def test_cors():
    return jsonify({
        'message': 'CORS test successful',
        'origins': ALLOWED_ORIGINS
    })

@app.route('/api/test-auth', methods=['GET'])
def test_auth():
    # Check Authorization header
    auth_header = request.headers.get('Authorization')
    
    # Print request details
    print("Headers received:")
    for header, value in request.headers.items():
        print(f"  {header}: {value}")
    
    result = {
        'authorization': auth_header is not None,
        'headers': dict(request.headers),
        'origins': ALLOWED_ORIGINS
    }
    
    if auth_header:
        # Split Bearer token
        parts = auth_header.split(' ')
        if len(parts) == 2:
            token_type, token = parts
            result['token_type'] = token_type
            result['token_length'] = len(token) if token else 0
            result['token_preview'] = token[:10] + '...' if token and len(token) > 10 else token
    
    return jsonify(result)

if __name__ == "__main__":
    print("CORS configuration:")
    print(f"Allowed origins: {ALLOWED_ORIGINS}")
    print("Running test server on http://localhost:5000")
    
    # Create a test uploads directory for serving files
    os.makedirs('uploads', exist_ok=True)
    with open('uploads/test-image.txt', 'w') as f:
        f.write('Test file to verify uploads directory is accessible')
    
    app.run(debug=True, host='0.0.0.0', port=5000) 