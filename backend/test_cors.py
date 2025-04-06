from flask import Flask, jsonify
from flask_cors import CORS
import os

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

if __name__ == "__main__":
    print("CORS configuration:")
    print(f"Allowed origins: {ALLOWED_ORIGINS}")
    print("Running test server on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000) 