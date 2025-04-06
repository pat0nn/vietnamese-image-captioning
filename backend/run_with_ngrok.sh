#!/bin/bash

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "Error: ngrok is not installed. Please install it from https://ngrok.com/download"
    exit 1
fi

# Set environment variables
export FLASK_APP=app.py
export FLASK_ENV=development

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
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
echo "✨ Use this URL when configuring your frontend environment:"
echo "NEXT_PUBLIC_API_URL=$NGROK_URL/api"
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