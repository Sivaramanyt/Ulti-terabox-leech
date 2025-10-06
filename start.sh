#!/bin/bash

echo "🚀 Starting Ultra Terabox Bot with Health Server..."

# Make sure aiohttp is available  
pip install aiohttp

# Start health server in background (correct path: bot/utils/)
echo "🏥 Starting health server on port 8000..."
python3 bot/utils/health_server.py &

# Wait a moment for health server to start
sleep 2

# Start the main bot
echo "🤖 Starting main bot..."
python3 -m bot

# Keep both running
wait
