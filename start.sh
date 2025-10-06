#!/bin/bash
# Start health server in background
python3 health_server.py &
# Start main bot
python3 -m bot
