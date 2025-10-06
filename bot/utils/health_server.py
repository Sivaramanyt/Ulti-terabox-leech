"""
Health check server for Koyeb compatibility
"""

from aiohttp import web
from config import LOGGER

async def health_check(request):
    return web.Response(text="Bot is running!", status=200)

async def start_health_server():
    """Start health check server for Koyeb"""
    app_web = web.Application()
    app_web.router.add_get('/', health_check)
    app_web.router.add_get('/health', health_check)
    
    runner = web.AppRunner(app_web)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8000)
    await site.start()
    LOGGER.info("Health check server started on port 8000")
