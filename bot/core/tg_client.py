from pyrogram import Client, idle
from config import BOT_TOKEN, TELEGRAM_API, TELEGRAM_HASH, LOGGER

class TgClient:
    bot = None
    
    @classmethod
    async def start_bot(cls):
        """Initialize and start the Telegram bot"""
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
