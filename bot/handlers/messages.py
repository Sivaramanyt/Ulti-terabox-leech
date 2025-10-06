"""
Bot message handlers - FIXED URL DETECTION
"""

from telegram import Update
from telegram.ext import ContextTypes
from config import LOGGER
from .processor import process_terabox_url

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle all text messages - FIXED TERABOX DETECTION"""
    user_id = update.effective_user.id
    message_text = update.message.text
    
    LOGGER.info(f"Message from {user_id}: {message_text}")
    print(f"📨 DEBUG: User {user_id} sent: {message_text}")
    
    # List of supported Terabox domains (EXACTLY LIKE ANASTY17)
    terabox_domains = [
        'terabox.com', 
        'teraboxurl.com', 
        '1024tera.com',
        'terasharelink.com',
        'momerybox.com',
        'tibibox.com'
    ]
    
    # Check if message contains Terabox URL (FIXED LOGIC)
    is_terabox_url = any(domain in message_text.lower() for domain in terabox_domains)
    
    if is_terabox_url:
        print(f"🎯 TERABOX URL DETECTED! Processing: {message_text}")
        LOGGER.info(f"Terabox URL detected: {message_text}")
        await process_terabox_url(update, message_text)
    else:
        # Echo for non-Terabox messages
        await update.message.reply_text(
            f"📢 **Echo:** {message_text}\n\n🆔 **Your ID:** `{user_id}`\n🤖 **I'm working!**\n\n**Send a Terabox URL to download!**",
            parse_mode='Markdown'
        )
        
