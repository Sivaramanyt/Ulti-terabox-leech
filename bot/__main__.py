"""
Ultra Terabox Bot - FINAL WORKING VERSION
Fixed all import issues + REAL Terabox Processing
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
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler

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

async def handle_message(update: Update, context):
    """Enhanced message handler with verification system"""
    try:
        user_id = update.effective_user.id
        message_text = update.message.text
        
        LOGGER.info(f"📨 Message from {update.effective_user.first_name} ({user_id})")
        
        # Check if message contains Terabox URL
        if is_terabox_url(message_text):
            LOGGER.info(f"📊 User {user_id} download #1")
            
            if VERIFICATION_AVAILABLE:
                try:
                    # Check if user needs verification
                    verification_required = await check_user_verification_required(user_id)
                    
                    if verification_required:
                        LOGGER.info(f"🔐 User {user_id} needs verification")
                        
                        # Send verification message
                        verification_button = InlineKeyboardButton(
                            "🔐 Click Here to Verify", 
                            callback_data=f"start_verification_{user_id}"
                        )
                        keyboard = InlineKeyboardMarkup([[verification_button]])
                        
                        await update.message.reply_text(
                            "🔐 **Verification Required**\n\n"
                            "You need to complete verification to access this feature.\n"
                            "Click the button below to start verification process.",
                            reply_markup=keyboard,
                            parse_mode='Markdown'
                        )
                        return
                    else:
                        LOGGER.info(f"✅ User {user_id} is verified, processing...")
                except Exception as e:
                    LOGGER.warning(f"⚠️ Verification check failed: {e}, proceeding without verification")
            
            # Process the Terabox URL
            await process_terabox_url(update, message_text)
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
    """Start command handler"""
    user_name = update.effective_user.first_name
    await update.message.reply_text(
        f"👋 **Welcome {user_name}!**\n\n"
        "🤖 **Ultra Terabox Bot**\n"
        "📥 Send me a Terabox link to download files!\n\n"
        "🔐 **Features:**\n"
        "• Fast Terabox downloads\n"
        "• User verification system\n"
        "• Auto-forward support\n\n"
        "💡 Just send any Terabox link to get started!",
        parse_mode='Markdown'
    )

async def help_command(update: Update, context):
    """Help command handler"""
    await update.message.reply_text(
        "🆘 **Help - Ultra Terabox Bot**\n\n"
        "**Commands:**\n"
        "• /start - Start the bot\n"
        "• /help - Show this help message\n\n"
        "**How to use:**\n"
        "1. Send any Terabox link\n"
        "2. Complete verification if required\n"
        "3. Get your downloaded file!\n\n"
        "**Supported links:**\n"
        "• terabox.com\n"  
        "• 1024tera.com\n"
        "• nephobox.com\n"
        "• mirrobox.com\n"
        "• And more Terabox domains",
        parse_mode='Markdown'
    )

async def handle_verification_token_input(update: Update, context):
    """Handle verification token input (fallback if verification module unavailable)"""
    if VERIFICATION_AVAILABLE:
        try:
            from bot.modules.token_verification import handle_verification_token_input as handle_token
            await handle_token(update, context)
        except Exception as e:
            LOGGER.error(f"❌ Verification token handling failed: {e}")
            await handle_message(update, context)
    else:
        # If no verification system, just process as normal message
        await handle_message(update, context)

async def main():
    """Main function"""
    try:
        LOGGER.info("🚀 Starting Ultra Terabox Bot...")
        
        # Create application
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Add command handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        
        # Add verification handlers if available
        if VERIFICATION_AVAILABLE:
            try:
                application.add_handler(CallbackQueryHandler(handle_verification_callbacks))
                LOGGER.info("✅ Verification callback handler registered")
            except Exception as e:
                LOGGER.error(f"❌ Failed to register verification handlers: {e}")
        
        # Add main message handler - this handles both verification token input and terabox processing
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_verification_token_input))
        
        LOGGER.info("✅ All handlers registered")
        LOGGER.info(f"🤖 Bot Token: {BOT_TOKEN[:20]}...")
        LOGGER.info(f"👤 Owner ID: {OWNER_ID}")
        LOGGER.info(f"🔐 Verification: {'ENABLED' if VERIFICATION_AVAILABLE else 'DISABLED'}")
        LOGGER.info("🟢 Bot starting...")
        LOGGER.info("🎯 Ready to process Terabox links!")
        
        # Start the bot
        await application.run_polling(drop_pending_updates=True)
        
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
    
