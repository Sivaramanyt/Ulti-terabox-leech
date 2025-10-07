"""
Enhanced Message Handlers with FIXED Verification - COMPLETE VERSION
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import *
import logging

LOGGER = logging.getLogger(__name__)

async def handle_terabox_with_verification(update: Update, terabox_url: str, user_id: int, context):
    """Handle Terabox URL with FIXED verification logic"""
    
    # Track download count
    if not hasattr(context.application, 'user_downloads'):
        context.application.user_downloads = {}
    
    current_downloads = context.application.user_downloads.get(user_id, 0)
    current_downloads += 1
    context.application.user_downloads[user_id] = current_downloads
    
    LOGGER.info(f"📊 User {user_id} download #{current_downloads}")
    
    # Check if verification is required
    if current_downloads > FREE_DOWNLOAD_LIMIT:
        LOGGER.info(f"🔐 User {user_id} needs verification (download #{current_downloads})")
        
        try:
            # Try to generate verification link
            verification_link = None
            
            try:
                from bot.modules.token_verification import generate_verification_link
                verification_link = await generate_verification_link(user_id)
            except Exception as e1:
                LOGGER.error(f"❌ Primary verification failed: {e1}")
                try:
                    from bot.modules.token_verification import create_verification_link
                    verification_link = create_verification_link(user_id)
                except Exception as e2:
                    LOGGER.error(f"❌ Secondary verification failed: {e2}")
            
            if verification_link:
                keyboard = [
                    [InlineKeyboardButton("🔐 Complete Verification", url=verification_link)],
                    [InlineKeyboardButton("ℹ️ Why Verification?", callback_data="why_verify")]
                ]
            else:
                keyboard = [
                    [InlineKeyboardButton("🔐 Start Verification", callback_data=f"start_verification_{user_id}")],
                    [InlineKeyboardButton("ℹ️ Why Verification?", callback_data="why_verify")]
                ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "🔐 **Verification Required**\n\n"
                f"You've reached your download limit ({current_downloads-1}/{FREE_DOWNLOAD_LIMIT} free downloads).\n\n"
                "**To continue downloading:**\n"
                "• Click the verification button below\n"
                "• Complete the quick verification\n"
                "• Get unlimited downloads!\n\n"
                "⏱️ **Verification takes only 30 seconds**",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return
            
        except Exception as e:
            LOGGER.error(f"❌ Verification system error: {e}")
            await update.message.reply_text(
                "❌ **Verification System Error**\n\n"
                f"Please contact support for assistance.",
                parse_mode='Markdown'
            )
            return
    else:
        LOGGER.info(f"✅ User {user_id} is within free limit ({current_downloads}/{FREE_DOWNLOAD_LIMIT})")
    
    # Process the Terabox URL (call your existing processor)
    from .processor import process_terabox_url
    await process_terabox_url(update, terabox_url)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Enhanced message handler with FIXED verification system"""
    user_id = update.effective_user.id
    message_text = update.message.text
    
    # Check for button responses
    if message_text in ["📞 Contact", "/contact"]:
        from .commands import contact_command
        await contact_command(update, context)
        return
    elif message_text in ["🆘 Help", "/help"]:
        from .commands import help_command
        await help_command(update, context)
        return
    elif message_text in ["📊 Status", "/status"]:
        from .commands import status_command
        await status_command(update, context)
        return
    elif message_text in ["ℹ️ About", "/about"]:
        from .commands import about_command
        await about_command(update, context)
        return
    
    LOGGER.info(f"📨 Message from {user_id}: {message_text}")
    print(f"📨 DEBUG: User {user_id} sent: {message_text}")

    # Check if message contains Terabox URL (enhanced detection)
    is_terabox_url = any(domain in message_text.lower() for domain in TERABOX_DOMAINS)

    if is_terabox_url:
        print(f"🎯 TERABOX URL DETECTED! Processing: {message_text}")
        LOGGER.info(f"Terabox URL detected: {message_text}")
        
        # Use enhanced verification system
        await handle_terabox_with_verification(update, message_text, user_id, context)
    else:
        # Try verification token handling first
        try:
            from bot.modules.token_verification import handle_verification_token_input
            await handle_verification_token_input(update, context)
            return
        except ImportError:
            pass
        except Exception as e:
            LOGGER.error(f"❌ Verification token handling failed: {e}")
        
        # Echo for non-Terabox messages
        await update.message.reply_text(
            f"📢 **Echo:** {message_text}\n\n🆔 **Your ID:** `{user_id}`\n🤖 **I'm working!**\n\n**Send a Terabox URL to download!**",
            parse_mode='Markdown'
                    )
                    
