from pyrogram.types import Message
from config import LOGGER

async def sendMessage(message: Message, text: str):
    """Send a message"""
    try:
        return await message.reply_text(text, disable_web_page_preview=True)
    except Exception as e:
        LOGGER.error(f"Send message error: {e}")
        return None

async def editMessage(message: Message, text: str):
    """Edit a message"""
    try:
        await message.edit_text(text, disable_web_page_preview=True)
    except Exception as e:
        LOGGER.error(f"Edit message error: {e}")
