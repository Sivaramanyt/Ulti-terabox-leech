"""
Callback Query Handlers for Inline Buttons
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, ContextTypes  
from config import *

LOGGER = logging.getLogger(__name__)

async def handle_callback_queries(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all callback queries from inline buttons"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "about":
        await handle_about_callback(query, context)
    elif query.data == "status":
        await handle_status_callback(query, context)
    elif query.data == "why_verify":
        await handle_why_verify_callback(query, context)
    elif query.data.startswith("start_verification"):
        await handle_start_verification_callback(query, context)
    else:
        # Handle verification system callbacks if available
        try:
            from bot.modules.token_verification import handle_verification_callbacks
            await handle_verification_callbacks(update, context)
        except ImportError:
            LOGGER.warning("Verification system not available for callback")
        except Exception as e:
            LOGGER.error(f"Verification callback error: {e}")

async def handle_about_callback(query, context):
    """Handle about callback"""
    await query.edit_message_text(
        "ℹ️ **About Ultra Terabox Bot**\n\n"
        "🔧 **Version:** 2.0\n"
        f"👨‍💻 **Developer:** {DEVELOPER_USERNAME}\n"
        "🚀 **Powered by:** Python & aiohttp\n"
        "☁️ **Hosted on:** Koyeb Cloud\n\n"
        "**Features:**\n"
        "• Ultra-fast downloads\n"
        "• Multiple domain support\n"
        "• User verification system\n"
        "• 24/7 uptime\n"
        "• Regular updates\n"
        f"• Free {FREE_DOWNLOAD_LIMIT} downloads per user\n\n"
        "**Made with ❤️ for the community**",
        parse_mode='Markdown'
    )

async def handle_status_callback(query, context):
    """Handle status callback"""
    import time
    uptime = time.time() - context.application.start_time if hasattr(context.application, 'start_time') else 0
    uptime_hours = int(uptime // 3600)
    uptime_minutes = int((uptime % 3600) // 60)
    
    try:
        from bot.modules.token_verification import check_user_verification_required
        verification_status = "Enabled"
    except ImportError:
        verification_status = "Disabled"
    
    await query.edit_message_text(
        "📊 **Bot Status**\n\n"
        f"🟢 **Status:** Online\n"
        f"⏰ **Uptime:** {uptime_hours}h {uptime_minutes}m\n"
        f"🔐 **Verification:** {verification_status}\n"
        f"📥 **Downloads:** Working\n"
        f"🤖 **API:** Functional\n"
        f"🆓 **Free Limit:** {FREE_DOWNLOAD_LIMIT} downloads per user\n\n"
        "**Last Update:** October 2025\n"
        "**Next Maintenance:** TBA",
        parse_mode='Markdown'
    )

async def handle_why_verify_callback(query, context):
    """Handle why verify callback"""
    await query.edit_message_text(
        "ℹ️ **Why Verification is Required**\n\n"
        f"**Free Usage:** {FREE_DOWNLOAD_LIMIT} downloads per user\n"
        "**After Verification:** Unlimited downloads\n\n"
        "**Why we need this:**\n"
        "• Prevent spam and abuse\n"
        "• Keep the service free for everyone\n"
        "• Maintain server costs\n\n"
        "**Quick & Safe:**\n"
        "• Takes only 30 seconds\n"
        "• No personal information required\n"
        "• One-time verification\n\n"
        "**Click verification button to continue**",
        parse_mode='Markdown'
    )

async def handle_start_verification_callback(query, context):
    """Handle start verification callback - FIXED VERSION"""
    user_id = int(query.data.split("_")[-1])
    
    try:
        # Try to generate verification link using multiple methods
        verification_link = None
        
        try:
            from bot.modules.token_verification import generate_verification_link
            verification_link = await generate_verification_link(user_id)
        except Exception as e1:
            LOGGER.error(f"❌ Primary verification method failed: {e1}")
            try:
                from bot.modules.token_verification import create_verification_link
                verification_link = create_verification_link(user_id)
            except Exception as e2:
                LOGGER.error(f"❌ Secondary verification method failed: {e2}")
                # Use fallback URL
                verification_link = f"{VERIFICATION_FALLBACK_URL}?user={user_id}"
        
        if verification_link:
            keyboard = [
                [InlineKeyboardButton("🔗 Complete Verification", url=verification_link)],
                [InlineKeyboardButton("ℹ️ Need Help?", url=SUPPORT_GROUP)]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                f"🔐 **Verification Link Generated**\n\n"
                f"**Step 1:** Click the verification button\n"
                f"**Step 2:** Complete the quick verification\n"
                f"**Step 3:** Return and send your Terabox link\n\n"
                f"**User ID:** {user_id}\n"
                f"**Time:** 30 seconds max\n\n"
                f"**After verification, you get unlimited downloads!**",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        else:
            await query.edit_message_text(
                "❌ **Verification System Error**\n\n"
                "Failed to generate verification link.\n"
                "Please contact support for manual verification.",
                parse_mode='Markdown'
            )
            
    except Exception as e:
        LOGGER.error(f"❌ Verification callback error: {e}")
        await query.edit_message_text(
            f"❌ **Verification Error**\n\n"
            f"Please contact support for assistance.",
            parse_mode='Markdown'
        )

def setup_callback_handlers(application):
    """Setup callback handlers"""
    application.add_handler(CallbackQueryHandler(handle_callback_queries))
    LOGGER.info("✅ Callback handlers registered")
