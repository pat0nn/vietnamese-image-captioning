#!/bin/bash

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "Error: ngrok is not installed. Please install it from https://ngrok.com/download"
    exit 1
fi

# Set environment variables
export FLASK_APP=app.py
export FLASK_ENV=development
export ALLOWED_ORIGINS="http://localhost:3000,https://icy-river-037493600.6.azurestaticapps.net"

# Print important information
echo "-------------------------------------------------------"
echo "🌐 Starting backend with CORS allowed for:"
echo "   - http://localhost:3000"
echo "   - https://icy-river-037493600.6.azurestaticapps.net"
echo "-------------------------------------------------------"

# Create uploads directory if it doesn't exist
mkdir -p uploads

# Create a test file in uploads for testing
echo "This is a test file to verify uploads directory access" > uploads/test-image.txt
echo "Created test file: uploads/test-image.txt"

# Start Flask in the background
echo "Starting Flask server..."
python app.py &
FLASK_PID=$!

# Wait for Flask to start
sleep 2

# Start ngrok
echo "Starting ngrok tunnel to port 5000..."
ngrok http 5000 > /dev/null &
NGROK_PID=$!

# Wait for ngrok to start
sleep 2

# Get the public URL
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o '"public_url":"[^"]*' | grep -o 'http[^"]*')

if [ -z "$NGROK_URL" ]; then
    echo "Error: Failed to get ngrok URL. Please check if ngrok is running correctly."
    kill $FLASK_PID
    kill $NGROK_PID
    exit 1
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 Backend API is now available at: $NGROK_URL/api"
echo "🌐 Images are now available at: $NGROK_URL/uploads"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
echo "✨ Use this URL when configuring your frontend environment:"
echo "NEXT_PUBLIC_API_URL=$NGROK_URL/api"
echo
echo "✨ LƯU Ý QUAN TRỌNG: Bạn cần xác nhận URL ngrok trước khi sử dụng!"
echo "   1. Mở trình duyệt và truy cập: $NGROK_URL/api/ngrok-ready"
echo "   2. Nhấn nút 'Visit Site' để xác nhận URL"
echo "   3. Tiếp tục truy cập: $NGROK_URL/uploads/test-image.txt"
echo "   4. Nhấn 'Visit Site' một lần nữa nếu thấy thông báo xác nhận"
echo "   5. Khi thấy văn bản 'This is a test file...', URL đã được xác nhận"
echo "   6. Mở trang kiểm tra: https://icy-river-037493600.6.azurestaticapps.net/test-ngrok"
echo "   7. Cập nhật URL trong Azure Portal nếu cần"
echo
echo "✨ Testing CORS configuration..."
curl -s -I -X OPTIONS -H "Origin: https://icy-river-037493600.6.azurestaticapps.net" \
    -H "Access-Control-Request-Method: GET" \
    -H "Access-Control-Request-Headers: Authorization, Content-Type" \
    "$NGROK_URL/api/test" | grep -i "access-control"
echo
echo "Press Ctrl+C to stop the server"

# Function to clean up on exit
cleanup() {
    echo "Stopping servers..."
    kill $FLASK_PID
    kill $NGROK_PID
    exit 0
}

# Set up the trap to catch Ctrl+C
trap cleanup SIGINT

# Wait for the user to press Ctrl+C
wait 