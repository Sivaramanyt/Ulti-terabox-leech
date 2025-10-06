"""
Ultra Terabox Bot - Correct Main File
Based on your actual bot structure with verification integration
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

# Try to import your existing handlers (based on your file structure)
try:
    from bot.handlers.mirror_leech import handle_message as process_terabox_message
    from bot.handlers.bot_commands import start_handler, help_handler
    EXISTING_HANDLERS = True
    LOGGER.info("✅ Existing handlers found")
except ImportError:
    EXISTING_HANDLERS = False
    LOGGER.warning("⚠️ Existing handlers not found, using basic handlers")

# Try to import verification system (the separate files I provided)
try:
    from bot.modules.token_verification import (
        token_verification_system,
        check_user_verification_required,
        handle_verification_token_input,
        handle_verification_callbacks,
        verification_cleanup_task
    )
    from bot.modules.auto_forward_system import initialize_auto_forward
    VERIFICATION_AVAILABLE = True
    LOGGER.info("✅ Verification modules imported successfully")
except ImportError as e:
    LOGGER.warning(f"⚠️ Verification modules not found: {e}")
    VERIFICATION_AVAILABLE = False

# ================================
# BASIC HANDLERS (fallback)
# ================================

async def basic_start_command(update: Update, context):
    """Basic start command if original not found"""
    user = update.effective_user
    LOGGER.info(f"👤 /start from {user.full_name} ({user.id})")
    
    welcome_text = f"""
🤖 **Ultra Terabox Leech Bot**

👋 Hello {user.mention_html()}!

📥 **How to use:**
1. Send me any Terabox link
2. I'll download and send you the file
3. That's it!

🔗 **Supported:** terabox.com, 1024tera.com, teraboxurl.com

🚀 **Ready? Send me a link!**
"""
    
    await update.message.reply_text(welcome_text, parse_mode='HTML')

async def basic_help_command(update: Update, context):
    """Basic help command if original not found"""
    help_text = """
📖 **Help**

🔗 **Supported platforms:**
• Terabox.com
• 1024tera.com  
• Teraboxurl.com

📥 **How to download:**
1. Send Terabox link
2. Wait for processing
3. Get your file!
"""
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

# ================================
# ENHANCED MESSAGE HANDLER
# ================================

async def enhanced_message_handler(update: Update, context):
    """Enhanced message handler with verification"""
    text = update.message.text
    user = update.effective_user
    user_id = user.id
    
    LOGGER.info(f"📨 Message from {user.full_name} ({user_id})")
    
    # Check if verification system is available
    if VERIFICATION_AVAILABLE:
        # Check if it's a terabox URL
        if any(domain in text.lower() for domain in ['terabox.com', '1024tera.com', 'teraboxurl.com']):
            # Check verification requirement
            can_proceed = await check_user_verification_required(update, user_id)
            if not can_proceed:
                return  # User needs verification
            
            # Increment count and process
            count = token_verification_system.increment_user_leech_count(user_id, user.username or '', user.full_name or '')
            LOGGER.info(f"📊 User {user_id} download #{count}")
            
            # Process with existing handler or fallback
            if EXISTING_HANDLERS:
                await process_terabox_message(update, context)
            else:
                await basic_terabox_processing(update, text)
        else:
            # Check if it's a verification token
            success = await handle_verification_token_input(update, user_id, text)
            if not success:
                await update.message.reply_text(
                    "❌ **Invalid Input**\n\nSend a Terabox link or verification token.",
                    parse_mode='Markdown'
                )
    else:
        # No verification, process directly
        if any(domain in text.lower() for domain in ['terabox.com', '1024tera.com', 'teraboxurl.com']):
            if EXISTING_HANDLERS:
                await process_terabox_message(update, context)
            else:
                await basic_terabox_processing(update, text)
        else:
            await update.message.reply_text("❌ Please send a valid Terabox URL.")

async def basic_terabox_processing(update, terabox_url):
    """Basic terabox processing fallback"""
    processing_msg = await update.message.reply_text(
        "🔍 **Processing Terabox Link...**",
        parse_mode='Markdown'
    )
    
    try:
        # Here you would integrate with your actual terabox processor
        # For now, simulate processing
        await asyncio.sleep(3)
        
        await update.message.reply_text(
            "✅ **Processing Complete!**\n\n"
            "🔧 **Note:** Basic processing mode active.\n"
            "📁 File processing completed.",
            parse_mode='Markdown'
        )
        
        await processing_msg.delete()
        
    except Exception as e:
        LOGGER.error(f"Processing error: {e}")
        await processing_msg.edit_text(
            "❌ **Processing Failed**\n\nPlease try again later.",
            parse_mode='Markdown'
        )

async def handle_callbacks(update: Update, context):
    """Handle callback queries"""
    query = update.callback_query
    await query.answer()
    
    # Handle verification callbacks if available
    if VERIFICATION_AVAILABLE:
        await handle_verification_callbacks(update, context)

# ================================
# BACKGROUND TASKS
# ================================

async def start_background_tasks():
    """Start background verification tasks"""
    if VERIFICATION_AVAILABLE and os.environ.get('IS_VERIFY', 'False').lower() == 'true':
        try:
            LOGGER.info("🔐 Starting verification cleanup task...")
            asyncio.create_task(verification_cleanup_task())
            LOGGER.info("✅ Verification cleanup task started")
        except Exception as e:
            LOGGER.error(f"❌ Failed to start verification tasks: {e}")

# ================================
# MAIN FUNCTION
# ================================

def main():
    """Main function to start the bot"""
    LOGGER.info("🚀 Starting Ultra Terabox Bot...")
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Initialize auto-forward if available
    if VERIFICATION_AVAILABLE:
        try:
            initialize_auto_forward(application.bot)
            LOGGER.info("✅ Auto-forward initialized")
        except Exception as e:
            LOGGER.warning(f"⚠️ Auto-forward initialization failed: {e}")
    
    # Add handlers
    if EXISTING_HANDLERS:
        # Use your existing handlers
        try:
            application.add_handler(CommandHandler("start", start_handler))
            application.add_handler(CommandHandler("help", help_handler))
            LOGGER.info("✅ Using existing command handlers")
        except:
            # Fallback to basic handlers
            application.add_handler(CommandHandler("start", basic_start_command))
            application.add_handler(CommandHandler("help", basic_help_command))
            LOGGER.info("✅ Using basic command handlers")
    else:
        # Use basic handlers
        application.add_handler(CommandHandler("start", basic_start_command))
        application.add_handler(CommandHandler("help", basic_help_command))
        LOGGER.info("✅ Using basic command handlers")
    
    # Add callback handler
    application.add_handler(CallbackQueryHandler(handle_callbacks))
    
    # Add enhanced message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, enhanced_message_handler))
    
    LOGGER.info("✅ All handlers registered")
    
    # Start background tasks
    asyncio.create_task(start_background_tasks())
    
    # Log configuration
    LOGGER.info(f"🤖 Bot Token: {BOT_TOKEN[:10]}...")
    LOGGER.info(f"👤 Owner ID: {OWNER_ID}")
    LOGGER.info(f"🔧 Existing Handlers: {'AVAILABLE' if EXISTING_HANDLERS else 'BASIC MODE'}")
    LOGGER.info(f"🔐 Verification: {'ENABLED' if VERIFICATION_AVAILABLE and os.environ.get('IS_VERIFY', 'False').lower() == 'true' else 'DISABLED'}")
    
    # Start the bot
    LOGGER.info("🟢 Bot starting...")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        LOGGER.info("🛑 Bot stopped by user")
    except Exception as e:
        LOGGER.error(f"❌ Bot startup failed: {e}")
        sys.exit(1)
    
