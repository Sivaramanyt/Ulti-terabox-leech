"""
Enhanced Message Handler with Token Verification
Integrates with existing processor without modifying it
"""

import asyncio
from telegram import Update
from config import LOGGER

# Import existing processor (your working code remains untouched)
from bot.handlers.processor import process_terabox_url as original_terabox_processor

# Import new verification system
from .token_verification import (
    token_verification_system,
    check_user_verification_required,
    handle_verification_token_input
)

# Import auto-forward system
from .auto_forward_system import auto_forward_user_file

async def enhanced_terabox_processor(update: Update, url: str):
    """Enhanced processor that adds verification + auto-forward to your existing code"""
    user_id = update.effective_user.id
    user_name = update.effective_user.full_name or "Unknown"
    username = update.effective_user.username or ""
    
    print(f"🔐 Enhanced processing for user {user_id}: {user_name}")
    LOGGER.info(f"Enhanced processing for user {user_id}: {user_name}")
    
    # First, check if this is a verification token (not a terabox URL)
    if not any(domain in url.lower() for domain in ['terabox.com', '1024tera.com', 'teraboxurl.com']):
        # This might be a verification token
        token_success = await handle_verification_token_input(update, user_id, url)
        if token_success:
            return  # Token was successfully processed
        # If not a token, fall through to regular processing
    
    # Check if verification is required for terabox URLs
    can_proceed = await check_user_verification_required(update, user_id)
    if not can_proceed:
        return  # User needs to verify first
    
    # User is verified or within free limit, increment count
    current_count = token_verification_system.increment_user_leech_count(user_id, username, user_name)
    print(f"📊 User {user_id} leech count: {current_count}")
    
    # Hook into your existing processor to add auto-forward functionality
    original_reply_video = update.message.reply_video
    original_reply_photo = update.message.reply_photo
    original_reply_document = update.message.reply_document
    
    async def enhanced_reply_video(*args, **kwargs):
        """Enhanced video reply with auto-forward"""
        message = await original_reply_video(*args, **kwargs)
        await auto_forward_user_file(message, user_id, user_name, username, 'video')
        return message
    
    async def enhanced_reply_photo(*args, **kwargs):
        """Enhanced photo reply with auto-forward"""
        message = await original_reply_photo(*args, **kwargs)
        await auto_forward_user_file(message, user_id, user_name, username, 'photo')
        return message
    
    async def enhanced_reply_document(*args, **kwargs):
        """Enhanced document reply with auto-forward"""
        message = await original_reply_document(*args, **kwargs)
        await auto_forward_user_file(message, user_id, user_name, username, 'document')
        return message
    
    # Temporarily replace the reply methods to intercept successful uploads
    update.message.reply_video = enhanced_reply_video
    update.message.reply_photo = enhanced_reply_photo
    update.message.reply_document = enhanced_reply_document
    
    try:
        # Call your original working processor (completely unchanged)
        await original_terabox_processor(update, url)
    finally:
        # Restore original methods
        update.message.reply_video = original_reply_video
        update.message.reply_photo = original_reply_photo
        update.message.reply_document = original_reply_document

async def enhanced_message_handler(update: Update, context):
    """Main message handler that replaces the one in your main.py"""
    text = update.message.text.strip()
    user_id = update.effective_user.id
    
    print(f"📨 Enhanced DEBUG: User {user_id} sent: {text[:50]}...")
    LOGGER.info(f"Enhanced message from user {user_id}")
    
    # Process all messages through enhanced processor
    await enhanced_terabox_processor(update, text)
