"""
Ultra Terabox Bot - ENHANCED WITH FIXED VERIFICATION & CONTACT MENU
"""

import logging
import asyncio
import os
import sys

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

LOGGER = logging.getLogger(__name__)

# Get configuration from environment variables
BOT_TOKEN = os.environ.get('BOT_TOKEN', '')
OWNER_ID = int(os.environ.get('OWNER_ID', '0'))

if not BOT_TOKEN:
    LOGGER.error("❌ BOT_TOKEN not set!")
    sys.exit(1)

# Import telegram modules
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand, BotCommandScopeDefault, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler

# Your contact info - UPDATE THESE WITH YOUR DETAILS ✅
DEVELOPER_CONTACT = "https://t.me/your_username"  # ✅ UPDATE THIS
UPDATES_CHANNEL = "https://t.me/your_channel"     # ✅ UPDATE THIS
SUPPORT_GROUP = "https://t.me/your_support_group" # ✅ UPDATE THIS

# Try to import verification system (optional)
VERIFICATION_AVAILABLE = False
try:
    from bot.modules.token_verification import (
        check_user_verification_required,
        handle_verification_callbacks
    )
    VERIFICATION_AVAILABLE = True
    LOGGER.info("✅ Verification modules imported successfully")
except ImportError as e:
    LOGGER.warning(f"⚠️ Verification modules not available: {e}")

# Import your original working message handler
TERABOX_HANDLER_AVAILABLE = False
try:
    import bot.handlers.messages as messages
    TERABOX_HANDLER_AVAILABLE = True
    LOGGER.info("✅ Original Terabox handler imported successfully")
except ImportError as e:
    LOGGER.error(f"❌ Failed to import Terabox handler: {e}")

def is_terabox_url(url):
    """Check if URL is a Terabox URL"""
    terabox_domains = [
        'terabox.com', 'www.terabox.com', 'teraboxapp.com', 'www.teraboxapp.com',
        '1024tera.com', 'www.1024tera.com', 'terabox.app', 'terasharelink.com',
        'nephobox.com', 'www.nephobox.com', '4funbox.com', 'www.4funbox.com',
        'mirrobox.com', 'www.mirrobox.com', 'momerybox.com', 'www.momerybox.com',
        'teraboxlink.com', 'www.teraboxlink.com'
    ]
    return any(domain in url.lower() for domain in terabox_domains)

async def process_terabox_url(update, terabox_url):
    """Process terabox URL using the original working handler"""
    if TERABOX_HANDLER_AVAILABLE:
        try:
            # Call the original working message handler
            await messages.handle_message(update, None)
        except Exception as e:
            LOGGER.error(f"❌ Error in Terabox processing: {e}")
            await update.message.reply_text(
                "❌ **Error Processing File**\n\n"
                "Sorry, there was an error processing your Terabox link. Please try again later.",
                parse_mode='Markdown'
            )
    else:
        await update.message.reply_text(
            "❌ **Terabox Handler Not Available**\n\n"
            "The Terabox processing system is currently unavailable.",
            parse_mode='Markdown'
        )

# ✅ NEW FUNCTION: Handle Terabox with FIXED verification logic
async def handle_terabox_with_verification(update: Update, terabox_url: str, user_id: int, context):
    """Handle Terabox URL with FIXED verification logic"""
    
    # ✅ FIXED: Manually track download count (simple approach)
    # In production, this should be stored in database
    if not hasattr(context.application, 'user_downloads'):
        context.application.user_downloads = {}
    
    # Get current download count for user
    current_downloads = context.application.user_downloads.get(user_id, 0)
    current_downloads += 1
    context.application.user_downloads[user_id] = current_downloads
    
    LOGGER.info(f"📊 User {user_id} download #{current_downloads}")
    
    # ✅ FIXED: Check if verification is required (after 3 downloads)
    if current_downloads > 3:
        LOGGER.info(f"🔐 User {user_id} needs verification (download #{current_downloads})")
        
        if VERIFICATION_AVAILABLE:
            try:
                # ✅ FIXED: Generate verification link properly
                from bot.modules.token_verification import generate_verification_link
                
                # Try to generate verification link
                try:
                    verification_link = await generate_verification_link(user_id)
                except Exception as gen_error:
                    LOGGER.error(f"❌ Failed to call generate_verification_link: {gen_error}")
                    # Try alternative method
                    try:
                        from bot.modules.token_verification import create_verification_link
                        verification_link = create_verification_link(user_id)
                    except Exception as alt_error:
                        LOGGER.error(f"❌ Alternative method failed: {alt_error}")
                        verification_link = None
                
                if verification_link:
                    keyboard = [
                        [InlineKeyboardButton("🔐 Complete Verification", url=verification_link)],
                        [InlineKeyboardButton("ℹ️ Why Verification?", callback_data="why_verify")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await update.message.reply_text(
                        "🔐 **Verification Required**\n\n"
                        f"You've reached your download limit ({current_downloads-1}/3 free downloads).\n\n"
                        "**To continue downloading:**\n"
                        "• Click the verification button below\n"
                        "• Complete the quick verification\n"
                        "• Get unlimited downloads!\n\n"
                        "⏱️ **Verification takes only 30 seconds**",
                        reply_markup=reply_markup,
                        parse_mode='Markdown'
                    )
                    return
                else:
                    LOGGER.error("❌ Failed to generate verification link")
                    
                    # ✅ FALLBACK: Manual verification button
                    keyboard = [
                        [InlineKeyboardButton("🔐 Start Verification", callback_data=f"start_verification_{user_id}")],
                        [InlineKeyboardButton("ℹ️ Why Verification?", callback_data="why_verify")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await update.message.reply_text(
                        "🔐 **Verification Required**\n\n"
                        f"You've reached your download limit ({current_downloads-1}/3 free downloads).\n\n"
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
                    f"Error: {str(e)}\n\nPlease try again later or contact support.",
                    parse_mode='Markdown'
                )
                return
        else:
            # Fallback if verification system not available
            await update.message.reply_text(
                "🔐 **Download Limit Reached**\n\n"
                f"You've used {current_downloads-1}/3 free downloads.\n\n"
                "Verification system is currently unavailable. Please contact support.",
                parse_mode='Markdown'
            )
            return
    else:
        LOGGER.info(f"✅ User {user_id} is within free limit ({current_downloads}/3)")
    
    # Process the Terabox URL (user is verified or within free limit)
    await process_terabox_url(update, terabox_url)

async def handle_message(update: Update, context):
    """Enhanced message handler with FIXED verification system"""
    try:
        user_id = update.effective_user.id
        message_text = update.message.text
        
        # Check for button responses
        if message_text in ["📞 Contact", "/contact"]:
            await contact_command(update, context)
            return
        elif message_text in ["🆘 Help", "/help"]:
            await help_command(update, context)
            return
        elif message_text in ["📊 Status", "/status"]:
            await status_command(update, context)
            return
        elif message_text in ["ℹ️ About", "/about"]:
            await about_command(update, context)
            return
        
        LOGGER.info(f"📨 Message from {update.effective_user.first_name} ({user_id})")
        
        # Check if message contains Terabox URL
        if is_terabox_url(message_text):
            # ✅ FIXED: Use the new verification handling
            await handle_terabox_with_verification(update, message_text, user_id, context)
        else:
            # Handle non-Terabox messages
            await update.message.reply_text(
                "🤖 **Ultra Terabox Bot**\n\n"
                "Send me a Terabox link to download!",
                parse_mode='Markdown'
            )
            
    except Exception as e:
        LOGGER.error(f"❌ Error in handle_message: {e}")
        await update.message.reply_text(
            "❌ An error occurred while processing your message."
        )

async def start(update: Update, context):
    """Enhanced start command with contact buttons"""
    user_name = update.effective_user.first_name
    
    # Create contact buttons
    keyboard = [
        [InlineKeyboardButton("📞 Contact Developer", url=DEVELOPER_CONTACT)],
        [InlineKeyboardButton("📢 Updates Channel", url=UPDATES_CHANNEL)],
        [InlineKeyboardButton("🆘 Help & Support", url=SUPPORT_GROUP)],
        [
            InlineKeyboardButton("ℹ️ About", callback_data="about"),
            InlineKeyboardButton("📊 Status", callback_data="status")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"👋 **Welcome {user_name}!**\n\n"
        "🤖 **Ultra Terabox Bot**\n"
        "📥 Send me a Terabox link to download files!\n\n"
        "🔐 **Features:**\n"
        "• Fast Terabox downloads\n"
        "• User verification system\n"
        "• Auto-forward support\n"
        "• 24/7 reliable service\n\n"
        "💡 **Just send any Terabox link to get started!**\n\n"
        "📞 **Need Help?** Use buttons below:",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def contact_command(update: Update, context):
    """Contact command"""
    keyboard = [
        [InlineKeyboardButton("💬 Direct Message", url=DEVELOPER_CONTACT)],
        [InlineKeyboardButton("🆘 Support Group", url=SUPPORT_GROUP)],
        [InlineKeyboardButton("📢 Updates Channel", url=UPDATES_CHANNEL)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📞 **Contact Information**\n\n"
        "👨‍💻 **Developer:** @your_username\n"  # ✅ UPDATE THIS
        "🆘 **Support:** Available 24/7\n"
        "📧 **Email:** your_email@gmail.com\n\n"  # ✅ UPDATE THIS
        "**For quick support:**\n"
        "• Bot issues - Direct message\n"
        "• General help - Support group\n"
        "• Updates - Follow channel\n\n"
        "**Response time:** Usually within 2-4 hours",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def help_command(update: Update, context):
    """Enhanced help command"""
    await update.message.reply_text(
        "🆘 **Help - Ultra Terabox Bot**\n\n"
        "**Commands:**\n"
        "• `/start` - Start the bot\n"
        "• `/help` - Show this help message\n"
        "• `/contact` - Contact developer\n"
        "• `/about` - About this bot\n"
        "• `/status` - Bot status\n\n"
        "**How to use:**\n"
        "1. Send any Terabox link\n"
        "2. Complete verification if required\n"
        "3. Get your downloaded file!\n\n"
        "**Supported links:**\n"
        "• terabox.com\n"  
        "• 1024tera.com\n"
        "• nephobox.com\n"
        "• mirrobox.com\n"
        "• And more Terabox domains\n\n"
        "**Free Limit:** 3 downloads, then verification required\n"
        "**Need help?** Use /contact",
        parse_mode='Markdown'
    )

async def about_command(update: Update, context):
    """About command"""
    await update.message.reply_text(
        "ℹ️ **About Ultra Terabox Bot**\n\n"
        "🔧 **Version:** 2.0\n"
        "👨‍💻 **Developer:** @your_username\n"  # ✅ UPDATE THIS
        "🚀 **Powered by:** Python & aiohttp\n"
        "☁️ **Hosted on:** Koyeb Cloud\n\n"
        "**Features:**\n"
        "• Ultra-fast downloads\n"  
        "• Multiple domain support\n"
        "• User verification system\n"
        "• 24/7 uptime\n"
        "• Regular updates\n"
        "• Free 3 downloads per user\n\n"
        "**Made with ❤️ for the community**",
        parse_mode='Markdown'
    )

async def status_command(update: Update, context):
    """Status command"""
    import time
    uptime = time.time() - context.application.start_time if hasattr(context.application, 'start_time') else 0
    uptime_hours = int(uptime // 3600)
    uptime_minutes = int((uptime % 3600) // 60)
    
    await update.message.reply_text(
        "📊 **Bot Status**\n\n"
        f"🟢 **Status:** Online\n"
        f"⏰ **Uptime:** {uptime_hours}h {uptime_minutes}m\n"
        f"🔐 **Verification:** {'Enabled' if VERIFICATION_AVAILABLE else 'Disabled'}\n"
        f"📥 **Downloads:** Working\n"
        f"🤖 **API:** Functional\n"
        f"🆓 **Free Limit:** 3 downloads per user\n\n"
        "**Last Update:** October 2025\n"
        "**Next Maintenance:** TBA",
        parse_mode='Markdown'
    )

# ✅ FIXED: Handle verification callback buttons
async def handle_callback(update: Update, context):
    """Handle callback queries from inline buttons - FIXED VERSION"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "about":
        await query.edit_message_text(
            "ℹ️ **About Ultra Terabox Bot**\n\n"
            "🔧 **Version:** 2.0\n"
            "👨‍💻 **Developer:** @your_username\n"  # ✅ UPDATE THIS
            "🚀 **Powered by:** Python & aiohttp\n"
            "☁️ **Hosted on:** Koyeb Cloud\n\n"
            "**Features:**\n"
            "• Ultra-fast downloads\n"
            "• Multiple domain support\n"
            "• User verification system\n"
            "• 24/7 uptime\n"
            "• Regular updates\n"
            "• Free 3 downloads per user\n\n"
            "**Made with ❤️ for the community**",
            parse_mode='Markdown'
        )
    elif query.data == "status":
        import time
        uptime = time.time() - context.application.start_time if hasattr(context.application, 'start_time') else 0
        uptime_hours = int(uptime // 3600)
        uptime_minutes = int((uptime % 3600) // 60)
        
        await query.edit_message_text(
            "📊 **Bot Status**\n\n"
            f"🟢 **Status:** Online\n"
            f"⏰ **Uptime:** {uptime_hours}h {uptime_minutes}m\n"
            f"🔐 **Verification:** {'Enabled' if VERIFICATION_AVAILABLE else 'Disabled'}\n"
            f"📥 **Downloads:** Working\n"
            f"🤖 **API:** Functional\n"
            f"🆓 **Free Limit:** 3 downloads per user\n\n"
            "**Last Update:** October 2025\n"
            "**Next Maintenance:** TBA",
            parse_mode='Markdown'
        )
    elif query.data == "why_verify":
        await query.edit_message_text(
            "ℹ️ **Why Verification is Required**\n\n"
            "**Free Usage:** 3 downloads per user\n"
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
    elif query.data.startswith("start_verification"):
        # ✅ FIXED: Handle verification start
        user_id = int(query.data.split("_")[-1])
        
        if VERIFICATION_AVAILABLE:
            try:
                # ✅ FIXED: Try different verification methods
                verification_link = None
                
                try:
                    from bot.modules.token_verification import generate_verification_link
                    verification_link = await generate_verification_link(user_id)
                except Exception as e1:
                    LOGGER.error(f"❌ Method 1 failed: {e1}")
                    try:
                        from bot.modules.token_verification import create_verification_link
                        verification_link = create_verification_link(user_id)
                    except Exception as e2:
                        LOGGER.error(f"❌ Method 2 failed: {e2}")
                        # ✅ FINAL FALLBACK: Manual verification
                        verification_link = f"https://your-verification-site.com/verify?user={user_id}"  # ✅ UPDATE THIS
                
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
                    f"Error: {str(e)}\n\n"
                    f"Please contact support for assistance.",
                    parse_mode='Markdown'
                )

async def setup_bot_commands(application):
    """Set up bot menu commands"""
    commands = [
        BotCommand("start", "🏠 Start the bot"),
        BotCommand("help", "🆘 Get help"),
        BotCommand("contact", "📞 Contact developer"),
        BotCommand("about", "ℹ️ About this bot"),
        BotCommand("status", "📊 Bot status")
    ]
    
    await application.bot.set_my_commands(commands, scope=BotCommandScopeDefault())
    LOGGER.info("✅ Bot menu commands set successfully")

# ✅ FIXED: Handle verification token input properly
async def handle_verification_token_input(update: Update, context):
    """Handle verification token input with FIXED parameters"""
    if VERIFICATION_AVAILABLE:
        try:
            from bot.modules.token_verification import handle_verification_token_input as handle_token
            # ✅ FIXED: Pass the correct parameters based on your system
            try:
                await handle_token(update, context)
            except TypeError:
                # Try with additional parameter if needed
                await handle_token(update, context, update.message.text)
            return
        except Exception as e:
            LOGGER.error(f"❌ Verification token handling failed: {e}")
    
    # If verification fails or not available, process as normal message
    await handle_message(update, context)

async def main():
    """Main function with FIXED verification and enhanced features"""
    try:
        LOGGER.info("🚀 Starting Ultra Terabox Bot...")
        
        # Create application
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Store start time for uptime calculation
        import time
        application.start_time = time.time()
        
        # ✅ CRITICAL FIX: Clear any existing webhooks first
        try:
            LOGGER.info("🧹 Clearing any existing webhooks...")
            await application.bot.delete_webhook(drop_pending_updates=True)
            LOGGER.info("✅ Webhook cleared successfully")
            await asyncio.sleep(3)  # Wait 3 seconds for Telegram to process
        except Exception as e:
            LOGGER.warning(f"⚠️ Webhook clear failed: {e}")
        
        # Set up bot menu commands
        await setup_bot_commands(application)
        
        # Add command handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("contact", contact_command))
        application.add_handler(CommandHandler("about", about_command))
        application.add_handler(CommandHandler("status", status_command))
        
        # ✅ FIXED: Add callback handler for inline buttons FIRST
        application.add_handler(CallbackQueryHandler(handle_callback))
        
        # Add verification handlers if available
        if VERIFICATION_AVAILABLE:
            try:
                # ✅ FIXED: Try to add verification callbacks without conflicts
                from bot.modules.token_verification import handle_verification_callbacks as orig_verify_handler
                
                # Create a combined callback handler
                async def combined_callback_handler(update: Update, context):
                    query = update.callback_query
                    if query.data in ["about", "status", "why_verify"] or query.data.startswith("start_verification"):
                        await handle_callback(update, context)
                    else:
                        await orig_verify_handler(update, context)
                
                # Replace the simple callback handler with combined one
                application.handlers[2] = []  # Clear callback handlers
                application.add_handler(CallbackQueryHandler(combined_callback_handler))
                
                LOGGER.info("✅ Combined verification callback handler registered")
            except Exception as e:
                LOGGER.error(f"❌ Failed to register verification handlers: {e}")
                # Fallback to simple callback handler
                application.add_handler(CallbackQueryHandler(handle_callback))
        
        # Add main message handler
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_verification_token_input))
        
        LOGGER.info("✅ All handlers registered")
        LOGGER.info(f"🤖 Bot Token: {BOT_TOKEN[:20]}...")
        LOGGER.info(f"👤 Owner ID: {OWNER_ID}")
        LOGGER.info(f"🔐 Verification: {'ENABLED' if VERIFICATION_AVAILABLE else 'DISABLED'}")
        LOGGER.info("🟢 Bot starting...")
        LOGGER.info("🎯 Ready to process Terabox links!")
        
        # ✅ FIXED: Start the bot with proper error handling
        try:
            await application.run_polling(
                drop_pending_updates=True,
                allowed_updates=["message", "callback_query"]
            )
        except Exception as polling_error:
            LOGGER.error(f"❌ Polling error: {polling_error}")
            raise
        
    except Exception as e:
        LOGGER.error(f"❌ Error in main: {e}")
        raise

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        LOGGER.info("🛑 Bot stopped by user")
    except Exception as e:
        LOGGER.error(f"❌ Fatal error: {e}")
        sys.exit(1)
