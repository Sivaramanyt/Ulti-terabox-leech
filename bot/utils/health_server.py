"""
Health check server for Koyeb compatibility - Fixed Import
"""

from aiohttp import web
import logging
import os

# Create logger directly instead of importing from config
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

async def health_check(request):
    """Health check endpoint"""
    return web.Response(text="Enhanced Terabox Bot is running!", status=200)

async def status_check(request):
    """Status endpoint with bot information"""
    try:
        # Try to check if enhanced mode is available
        mode = "Standard Reliable Mode"
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
    
    # Use PORT environment variable or default to 8000
    port = int(os.environ.get('PORT', 8000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    LOGGER.info(f"Health check server started on port {port}")

if __name__ == "__main__":
    import asyncio
    try:
        LOGGER.info("🏥 Starting health check server...")
        asyncio.run(start_health_server())
        
        # Keep server running
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        LOGGER.info("🛑 Health server stopped")
    
