"""
Health Server for Bot
"""

import asyncio
import logging
from aiohttp import web

LOGGER = logging.getLogger(__name__)

async def health_check(request):
    """Health check endpoint"""
    return web.json_response({
        "status": "healthy",
        "service": "ultra-terabox-bot",
        "timestamp": str(asyncio.get_event_loop().time())
    })

async def start_health_server():
    """Start health check server"""
    try:
        app = web.Application()
        app.router.add_get('/health', health_check)
        app.router.add_get('/', health_check)
        
        # Start server on port 8000
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', 8000)
        await site.start()
        
        LOGGER.info("✅ Health server started on port 8000")
        return runner
        
    except Exception as e:
        LOGGER.error(f"❌ Health server failed: {e}")
        return None
        
