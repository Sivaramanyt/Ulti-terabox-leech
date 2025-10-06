"""
Health check server for Koyeb compatibility - Enhanced Edition
Starts both health server and bot together
"""

from aiohttp import web
import aiohttp
import asyncio
import os
from config import LOGGER

async def health_check(request):
    """Health check endpoint"""
    return web.Response(text="Enhanced Terabox Bot is running!", status=200)

async def status_check(request):
    """Status endpoint with bot information"""
    try:
        # Try to check if enhanced mode is available
        mode = "Enhanced Multi-Connection Mode"
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
    
    LOGGER.info(f"🌐 Health check server started on port {port}")

async def start_bot():
    """Start the main bot"""
    try:
        # Import and run bot
        LOGGER.info("🤖 Starting main bot...")
        from bot import main
        await main()
    except Exception as e:
        LOGGER.error(f"❌ Bot startup failed: {e}")

async def run_both():
    """Run both health server and bot"""
    # Start health server
    await start_health_server()
    
    # Start bot
    await start_bot()

if __name__ == "__main__":
    try:
        LOGGER.info("🚀 Starting Enhanced Terabox Bot with Health Server...")
        asyncio.run(run_both())
    except KeyboardInterrupt:
        LOGGER.info("🛑 Shutting down...")
    except Exception as e:
        LOGGER.error(f"❌ Startup failed: {e}")
        
