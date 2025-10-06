from . import LOGGER, bot_loop
from .core.tg_client import TgClient
from config import *

async def main():
    """Main bot function"""
    try:
        # Start the Telegram client
        await TgClient.start_bot()
        
        # Import modules after client is ready
        from .modules import leech
        
        LOGGER.info("✅ Terabox Leech Bot started successfully!")
        
        # Keep the bot running
        await TgClient.idle()
        
    except Exception as e:
        LOGGER.error(f"Bot startup error: {e}")
        raise

if __name__ == "__main__":
    bot_loop.run_until_complete(main())
