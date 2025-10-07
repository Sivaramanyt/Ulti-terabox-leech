"""
Simple HTTP Health Server for Koyeb
"""
import http.server
import socketserver
import threading
import logging
import json
from urllib.parse import urlparse

LOGGER = logging.getLogger(__name__)

class HealthHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path in ['/', '/health']:
            # Health check endpoint
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {
                "status": "healthy",
                "service": "ultra-terabox-bot",
                "message": "Bot is running perfectly!",
                "port": 8000
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            # 404 for other paths
            self.send_error(404, "Not Found")
    
    def log_message(self, format, *args):
        # Suppress default HTTP server logs
        pass

def start_health_server():
    """Start HTTP health server on port 8000"""
    try:
        with socketserver.TCPServer(("0.0.0.0", 8000), HealthHandler) as httpd:
            LOGGER.info("✅ Health server started on port 8000 (HTTP)")
            httpd.serve_forever()
    except Exception as e:
        LOGGER.error(f"❌ Health server failed: {e}")

def start_health_background():
    """Start health server in background thread"""
    try:
        health_thread = threading.Thread(target=start_health_server, daemon=True)
        health_thread.start()
        LOGGER.info("✅ Health server thread started")
        
        # Give it time to start
        import time
        time.sleep(2)
        return True
    except Exception as e:
        LOGGER.error(f"❌ Health server thread failed: {e}")
        return False
            
