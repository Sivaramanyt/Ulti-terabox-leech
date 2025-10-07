"""
Enhanced Message Handler with VJ Verification System & Validity Time Display
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import *
from bot.utils.token_verification import (
    generate_verification_link, 
    check_verification, 
    verify_user_token,
    get_user_download_count,
    increment_user_downloads,
    get_verification_info,
    VALIDITY_TIME_TEXT
)

LOGGER = logging.getLogger(__name__)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enhanced message handler with verification"""
    message = update.message
    user_id = message.from_user.id
    text = message.text.strip()
    
    # Log all messages for debugging
    LOGGER.info(f"Message from user {user_id}: {text[:50]}...")
    
    # Check if it's a Terabox URL
    if any(domain in text.lower() for domain in ['terabox.com', '1024tera.com', 'teraboxapp.com', 'nephobox.com', 'mirrobox.com', 'terabox.app']):
        await handle_terabox_url(update, context)
    else:
        await message.reply_text(
            "🔗 **Send a Terabox link to download**\n\n"
            "**Supported formats:**\n"
            "• terabox.com/s/...\n"
            "• 1024tera.com/s/...\n"
            "• teraboxapp.com/s/...\n\n"
            "**Commands:**\n"
            "• /start - Bot information\n"
            "• /leech - Standard download\n"
            "• /fast - Enhanced download",
            parse_mode='Markdown'
        )

async def handle_terabox_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Terabox URL with verification check"""
    message = update.message
    user_id = message.from_user.id
    terabox_url = message.text.strip()
    
    # Check user verification status
    if VERIFY:
        user_downloads = get_user_download_count(user_id)
        is_verified = check_verification(user_id)
        
        if user_downloads >= FREE_DOWNLOAD_LIMIT and not is_verified:
            await send_verification_required_message(message, user_id, user_downloads)
            return
    
    # Process the Terabox URL
    try:
        from bot.handlers.processor import process_terabox_url
        await process_terabox_url(update, context)
    except ImportError:
        await message.reply_text("❌ **Processor module not available**")
        LOGGER.error("Processor module not found")

async def send_verification_required_message(message, user_id, download_count):
    """Send VJ-style verification message with validity time info"""
    try:
        # Generate verification link
        verify_link = generate_verification_link(user_id)
        
        if verify_link:
            keyboard = [
                [InlineKeyboardButton("🔗 Click Here to Verify", url=verify_link)],
                [InlineKeyboardButton("❓ How to Verify?", url=VERIFY_TUTORIAL)],
                [InlineKeyboardButton("♻️ Refresh Status", callback_data=f"refresh_verification_{user_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await message.reply_text(
                f"🔐 **Verification Required**\n\n"
                f"You've used **{download_count}/{FREE_DOWNLOAD_LIMIT}** free downloads.\n\n"
                f"**To get unlimited downloads:**\n"
                f"1. Click the verification link below\n"
                f"2. Complete the shortlink (10-20 seconds)\n"
                f"3. You'll see 'Your Link is Ready' message\n"
                f"4. Click the final link to return to bot\n\n"
                f"✅ **Valid for {VALIDITY_TIME_TEXT}**\n"
                f"🎯 **VJ Verification System**",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await message.reply_text(
                "❌ **Verification system temporarily unavailable.**\n"
                "Please try again in a few minutes.",
                parse_mode='Markdown'
            )
    except Exception as e:
        LOGGER.error(f"Error sending verification message: {e}")
        await message.reply_text(
            "❌ **Error generating verification link**\n"
            "Please contact support.",
            parse_mode='Markdown'
        )

async def handle_start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enhanced start command with verification support and validity time"""
    message = update.message
    user_id = message.from_user.id
    
    # Check if it's a verification start
    if context.args and len(context.args) > 0:
        arg = context.args[0]
        if arg.startswith('verify_'):
            token = arg.replace('verify_', '')
            success, verified_user_id = verify_user_token(token)
            
            if success:
                await message.reply_text(
                    "✅ **Verification Successful!**\n\n"
                    "🎉 You now have unlimited downloads!\n"
                    "📤 Send any Terabox link to start downloading.\n\n"
                    f"🕐 **Validity:** {VALIDITY_TIME_TEXT}\n"
                    "🚀 **VJ Verification System - Activated**",
                    parse_mode='Markdown'
                )
                return
            else:
                await message.reply_text(
                    "❌ **Verification Failed**\n\n"
                    "Token expired or invalid.\n"
                    f"Tokens are valid for {VALIDITY_TIME_TEXT}.\n"
                    "Please request a new verification link.",
                    parse_mode='Markdown'
                )
                return
    
    # Regular start message with verification info
    user_downloads = get_user_download_count(user_id)
    verification_info = get_verification_info(user_id)
    
    if verification_info['verified']:
        status_text = f"✅ **Verified** (Valid for {VALIDITY_TIME_TEXT})"
    else:
        status_text = f"📊 **{user_downloads}/{FREE_DOWNLOAD_LIMIT}** downloads used"
    
    keyboard = [
        [InlineKeyboardButton("📖 About", callback_data="about"),
         InlineKeyboardButton("📊 Status", callback_data="status")],
        [InlineKeyboardButton("❓ Why Verify?", callback_data="why_verify")]
    ]
    
    if not verification_info['verified'] and user_downloads >= FREE_DOWNLOAD_LIMIT:
        keyboard.insert(0, [InlineKeyboardButton("🔓 Start Verification", callback_data=f"start_verification_{user_id}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await message.reply_text(
        f"🚀 **Ultra Terabox Bot with VJ Verification**\n\n"
        f"👋 **Welcome:** {message.from_user.first_name}\n"
        f"🔐 **Status:** {status_text}\n\n"
        f"**📋 How to use:**\n"
        f"• Send any Terabox link\n"
        f"• Get instant downloads\n"
        f"• Use /leech or /fast commands\n\n"
        f"**🕐 Verification Validity:** {VALIDITY_TIME_TEXT}\n"
        f"**🎯 VJ Verification System Active**",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
