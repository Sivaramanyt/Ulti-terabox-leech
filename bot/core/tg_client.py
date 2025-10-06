from pyrogram import Client, idle
from config import BOT_TOKEN, TELEGRAM_API, TELEGRAM_HASH, LOGGER
import os
import glob

class TgClient:
    bot = None
    
    @classmethod
    async def start_bot(cls):
        """Initialize and start the Telegram bot"""
        
        # Clean up any existing session files to prevent FLOOD_WAIT
        session_patterns = [
            "terabox_bot.session*",
            "*.session*"
        ]
        
        for pattern in session_patterns:
            for file in glob.glob(pattern):
                try:
                    os.remove(file)
                    LOGGER.info(f"Cleaned session file: {file}")
                except:
                    pass
        
        cls.bot = Client(
            "terabox_bot",
            api_id=TELEGRAM_API,
            api_hash=TELEGRAM_HASH,
            bot_token=BOT_TOKEN
        )
        
        await cls.bot.start()
        LOGGER.info("Telegram bot client started")
        
    @classmethod
    async def idle(cls):
        """Keep the bot running"""
        await idle()
        
    @classmethod
    async def stop(cls):
        """Stop the bot"""
        if cls.bot:
            await cls.bot.stop()
        
