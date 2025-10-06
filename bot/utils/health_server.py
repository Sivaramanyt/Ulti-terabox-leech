from aiohttp import web
import asyncio
import logging
import os

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

async def health_check(request):
    return web.Response(text="OK", status=200)

async def status_check(request):
    return web.json_response({"status": "running", "bot": "Ultra Terabox Bot"})

if __name__ == "__main__":
    app = web.Application()
    app.router.add_get('/', health_check)
    app.router.add_get('/health', health_check)
    app.router.add_get('/status', status_check)
    
    port = int(os.environ.get('PORT', 8000))
    LOGGER.info(f"Starting health server on port {port}")
    
    web.run_app(app, host='0.0.0.0', port=port)
    
