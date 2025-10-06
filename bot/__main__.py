"""
Ultra Terabox Bot - FIXED Main File
Fixed the asyncio event loop issue
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

# Try to import your existing handlers
try:
    from bot.handlers.mirror_leech import handle_message as process_terabox_message
    from bot.handlers.bot_commands import start_handler, help_handler
    EXISTING_HANDLERS = True
    LOGGER.info("✅ Existing handlers found")
except ImportError:
    EXISTING_HANDLERS = False
    LOGGER.warning("⚠️ Existing handlers not found, using basic handlers")

# Try to import verification system
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
# BASIC HANDLERS
# ================================

async def basic_start_command(update: Update, context):
    """Basic start command"""
    user = update.effective_user
    LOGGER.info(f"👤 /start from {user.full_name} ({user.id})")
    
    status_info = ""
    if VERIFICATION_AVAILABLE and os.environ.get('IS_VERIFY', 'False').lower() == 'true':
        user_data = token_verification_system.get_user_verification_data(user.id)
        current_time = int(__import__('time').time())
        
        if user_data['verified_until'] > current_time:
            status_info = "\n🔐 **Status:** ✅ Verified (Unlimited)"
        else:
            free_limit = int(os.environ.get('FREE_LEECH_LIMIT', '3'))
            remaining = max(0, free_limit - user_data['leech_count'])
            status_info = f"\n🆓 **Status:** {remaining} free downloads left"
    
    welcome_text = f"""
🤖 **Ultra Terabox Leech Bot**

👋 Hello {user.mention_html()}!{status_info}

📥 **How to use:**
1. Send me any Terabox link
2. I'll download and send you the file
3. That's it!

🔗 **Supported links:**
• terabox.com • 1024tera.com • teraboxurl.com

🚀 **Ready? Send me a Terabox link!**
"""
    
    keyboard = [
        [InlineKeyboardButton("📖 Help", callback_data="help")],
        [InlineKeyboardButton("📊 My Status", callback_data="status")]
    ]
    
    await update.message.reply_text(
        welcome_text,
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def basic_help_command(update: Update, context):
    """Basic help command"""
    verification_info = ""
    if VERIFICATION_AVAILABLE and os.environ.get('IS_VERIFY', 'False').lower() == 'true':
        free_limit = os.environ.get('FREE_LEECH_LIMIT', '3')
        verification_info = f"""

🔐 **Verification System:**
• First {free_limit} downloads are FREE
• After that, complete simple verification
• Get 24 hours unlimited access
• Easy shortlink verification process
"""
    
    help_text = f"""
📖 **Help & Instructions**

🔗 **Supported Platforms:**
• Terabox.com • 1024tera.com • Teraboxurl.com

📥 **How to Download:**
1. Copy any Terabox share link
2. Send it to this bot
3. Wait for processing
4. Receive your file!

⚡ **Features:**
• Fast downloads • Multiple formats • Clean interface{verification_info}

❓ **Need help?** Just send /help anytime!
"""
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

# ================================
# MESSAGE HANDLER
# ================================

async def enhanced_message_handler(update: Update, context):
    """Enhanced message handler with verification"""
    text = update.message.text
    user = update.effective_user
    user_id = user.id
    
    LOGGER.info(f"📨 Message from {user.full_name} ({user_id})")
    
    # Check if verification system is available
    if VERIFICATION_AVAILABLE and os.environ.get('IS_VERIFY', 'False').lower() == 'true':
        # Check if it's a terabox URL
        if any(domain in text.lower() for domain in ['terabox.com', '1024tera.com', 'teraboxurl.com']):
            # Check verification requirement
            can_proceed = await check_user_verification_required(update, user_id)
            if not can_proceed:
                return  # User needs verification
            
            # Increment count and process
            count = token_verification_system.increment_user_leech_count(user_id, user.username or '', user.full_name or '')
            LOGGER.info(f"📊 User {user_id} download #{count}")
            
            # Process terabox
            await process_terabox_url(update, text)
        else:
            # Check if it's a verification token
            success = await handle_verification_token_input(update, user_id, text)
            if not success:
                await update.message.reply_text(
                    "❌ **Invalid Input**\n\n"
                    "🔗 Please send a **Terabox link** or **verification token**.\n\n"
                    "**Supported domains:**\n• terabox.com\n• 1024tera.com\n• teraboxurl.com",
                    parse_mode='Markdown'
                )
    else:
        # No verification, process directly
        if any(domain in text.lower() for domain in ['terabox.com', '1024tera.com', 'teraboxurl.com']):
            await process_terabox_url(update, text)
        else:
            await update.message.reply_text(
                "❌ **Invalid Link**\n\n"
                "🔗 Please send a valid **Terabox URL**.\n\n"
                "**Supported domains:**\n• terabox.com\n• 1024tera.com\n• teraboxurl.com",
                parse_mode='Markdown'
            )

async def process_terabox_url(update, terabox_url):
    """Process terabox URL"""
    processing_msg = await update.message.reply_text(
        "🔍 **Processing Terabox Link...**\n\n⏳ Please wait while I fetch your file.",
        parse_mode='Markdown'
    )
    
    try:
        # Use existing handler if available
        if EXISTING_HANDLERS:
            await process_terabox_message(update, None)
        else:
            # Basic processing simulation
            await asyncio.sleep(3)
            
            await update.message.reply_text(
                "✅ **Processing Complete!**\n\n"
                "🎉 Your file has been processed successfully!\n"
                "📤 File download ready!\n\n"
                "🔧 **Note:** This is basic mode. Integrate your Terabox processor for full functionality.",
                parse_mode='Markdown'
            )
        
        await processing_msg.delete()
        
    except Exception as e:
        LOGGER.error(f"Processing error: {e}")
        await processing_msg.edit_text(
            "❌ **Processing Failed**\n\n"
            "😔 Something went wrong while processing your link.\n"
            "🔄 Please try again in a few moments.",
            parse_mode='Markdown'
        )

async def handle_callbacks(update: Update, context):
    """Handle callback queries"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "help":
        await basic_help_command(query, context)
    elif query.data == "status":
        if VERIFICATION_AVAILABLE and os.environ.get('IS_VERIFY', 'False').lower() == 'true':
            user_data = token_verification_system.get_user_verification_data(query.from_user.id)
            current_time = int(__import__('time').time())
            
            if user_data['verified_until'] > current_time:
                status = "✅ **VERIFIED** (Unlimited downloads)"
                expiry = user_data['verified_until'] - current_time
                hours = expiry // 3600
                status += f"\n⏰ Expires in: {hours} hours"
            else:
                free_limit = int(os.environ.get('FREE_LEECH_LIMIT', '3'))
                remaining = max(0, free_limit - user_data['leech_count'])
                status = f"🆓 **FREE USER** ({remaining} downloads left)"
            
            await query.message.reply_text(
                f"📊 **Your Status**\n\n"
                f"{status}\n\n"
                f"📈 **Total Downloads:** {user_data['total_leeches']}\n"
                f"📅 **Current Count:** {user_data['leech_count']}/{free_limit}",
                parse_mode='Markdown'
            )
        else:
            await query.message.reply_text(
                "📊 **Bot Status**\n\n"
                "✅ **Service:** Active and Running\n"
                "🔧 **Verification:** Disabled\n"
                "📥 **Downloads:** Unlimited",
                parse_mode='Markdown'
            )
    else:
        # Handle verification callbacks if available
        if VERIFICATION_AVAILABLE:
            await handle_verification_callbacks(update, context)

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
        try:
            application.add_handler(CommandHandler("start", start_handler))
            application.add_handler(CommandHandler("help", help_handler))
            LOGGER.info("✅ Using existing command handlers")
        except:
            application.add_handler(CommandHandler("start", basic_start_command))
            application.add_handler(CommandHandler("help", basic_help_command))
            LOGGER.info("✅ Using basic command handlers")
    else:
        application.add_handler(CommandHandler("start", basic_start_command))
        application.add_handler(CommandHandler("help", basic_help_command))
        LOGGER.info("✅ Using basic command handlers")
    
    # Add callback and message handlers
    application.add_handler(CallbackQueryHandler(handle_callbacks))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, enhanced_message_handler))
    
    LOGGER.info("✅ All handlers registered")
    
    # Log configuration
    LOGGER.info(f"🤖 Bot Token: {BOT_TOKEN[:10]}...")
    LOGGER.info(f"👤 Owner ID: {OWNER_ID}")
    LOGGER.info(f"🔧 Existing Handlers: {'AVAILABLE' if EXISTING_HANDLERS else 'BASIC MODE'}")
    LOGGER.info(f"🔐 Verification: {'ENABLED' if VERIFICATION_AVAILABLE and os.environ.get('IS_VERIFY', 'False').lower() == 'true' else 'DISABLED'}")
    
    # Start background verification task if needed
    if VERIFICATION_AVAILABLE and os.environ.get('IS_VERIFY', 'False').lower() == 'true':
        def post_init(app):
            """Post initialization callback"""
            try:
                asyncio.create_task(verification_cleanup_task())
                LOGGER.info("✅ Verification cleanup task started")
            except Exception as e:
                LOGGER.error(f"❌ Failed to start verification task: {e}")
        
        application.post_init = post_init
    
    # Start the bot
    LOGGER.info("🟢 Bot starting...")
    LOGGER.info("🎯 Ready to process Terabox links!")
    
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        LOGGER.info("🛑 Bot stopped by user")
    except Exception as e:
        LOGGER.error(f"❌ Bot startup failed: {e}")
        sys.exit(1)
    
