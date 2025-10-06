"""
Bot message handlers
"""

from telegram import Update
from telegram.ext import ContextTypes
from config import LOGGER
from .processor import process_terabox_url

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo messages and handle supported URLs"""
    user_id = update.effective_user.id
    message_text = update.message.text
    
    LOGGER.info(f"Message from {user_id}: {message_text}")
    print(f"📨 DEBUG: User {user_id} sent: {message_text}")
    
    # Supported domains for auto-detection
    supported_domains = [
        'terabox.com', 
        'teraboxurl.com', 
        'terasharelink.com',
        '1024tera.com',
        'momerybox.com',
        'tibibox.com',
        '4funbox.co'
    ]
    
    # Check if message contains supported URL
    is_supported_url = any(domain in message_text.lower() for domain in supported_domains)
    
    if is_supported_url:
        await process_terabox_url(update, message_text)
    else:
        await update.message.reply_text(
            f"📢 **Echo:** {message_text}\n\n🆔 **Your ID:** `{user_id}`\n🤖 **I'm working!**\n\n**Supported domains:**\n• terabox.com\n• teraboxurl.com\n• terasharelink.com",
            parse_mode='Markdown'
        )
