"""
Ultra Simple Terabox Leech Bot - Main Entry
Modular structure with separate files
"""

import asyncio
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config import BOT_TOKEN, LOGGER
from .utils.health_server import start_health_server
from .handlers.commands import start, test_handler, leech_command
from .handlers.messages import echo

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

async def main():
    """Main function"""
    try:
        # Start health check server
        await start_health_server()
        
        # Create application
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("test", test_handler))
        application.add_handler(CommandHandler("leech", leech_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
        
        print(f"🚀 Bot starting with token: {BOT_TOKEN[:20]}...")
        print(f"🌐 Health check server running on port 8000")
        print(f"🔍 DEBUG MODE: All messages will be logged")
        
        # Start the bot
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        
        LOGGER.info("✅ Bot started successfully!")
        print("✅ Bot is now running with WORKING leech functionality!")
        
        # Keep running
        while True:
            await asyncio.sleep(1)
            
    except Exception as e:
        LOGGER.error(f"❌ Bot startup error: {e}")
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(main())
    
