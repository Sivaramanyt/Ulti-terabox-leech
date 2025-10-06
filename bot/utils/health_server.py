"""
Health check server for Koyeb compatibility - Enhanced Edition
"""

from aiohttp import web
from config import LOGGER

async def health_check(request):
    """Health check endpoint"""
    return web.Response(text="Enhanced Terabox Bot is running!", status=200)

async def status_check(request):
    """Status endpoint with bot information"""
    try:
        # Try to check if enhanced mode is available
        try:
            import bot.handlers.enhanced_processor
            mode = "Enhanced Multi-Connection Mode"
        except ImportError:
            mode = "Standard Reliable Mode"
        
        status_info = {
            "status": "running",
            "mode": mode,
            "bot": "Ultra Terabox Leech Bot",
            "version": "2.0 Enhanced Edition"
        }
        
        return web.json_response(status_info)
    except Exception as e:
        return web.json_response({"status": "error", "message": str(e)}, status=500)

async def start_health_server():
    """Start health check server for Koyeb"""
    app_web = web.Application()
    app_web.router.add_get('/', health_check)
    app_web.router.add_get('/health', health_check)
    app_web.router.add_get('/status', status_check)
    
    runner = web.AppRunner(app_web)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8000)
    await site.start()
    LOGGER.info("Health check server started on port 8000")
    
