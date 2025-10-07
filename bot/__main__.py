"""
Ultra Simple Terabox Leech Bot - WORKING VERSION
Fixed health server import and event loop handling
"""

import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from telegram import BotCommand, BotCommandScopeDefault
from config import BOT_TOKEN, LOGGER, OWNER_ID

# Try to import your handlers
try:
    import bot.handlers.commands as commands
    commands_available = True
except ImportError as e:
    LOGGER.error(f"Commands not available: {e}")
    commands_available = False

try:
    import bot.handlers.messages as messages
    messages_available = True
except ImportError as e:
    LOGGER.error(f"Messages handler not available: {e}")
    messages_available = False

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def setup_bot_commands(application):
    """Set up bot menu commands"""
    try:
        commands_list = [
            BotCommand("start", "🏠 Start the bot"),
            BotCommand("help", "🆘 Get help"),
            BotCommand("contact", "📞 Contact developer"),
            BotCommand("about", "ℹ️ About this bot"),
            BotCommand("status", "📊 Bot status"),
            BotCommand("test", "🧪 Test bot"),
            BotCommand("leech", "📥 Download files")
        ]
        
        await application.bot.set_my_commands(commands_list, scope=BotCommandScopeDefault())
        LOGGER.info("✅ Bot menu commands set successfully")
    except Exception as e:
        LOGGER.error(f"❌ Failed to set bot commands: {e}")

# ✅ SIMPLE FALLBACK HANDLERS (in case imports fail)
async def simple_start(update, context):
    """Simple start command"""
    user_name = update.effective_user.first_name
    await update.message.reply_text(
        f"👋 **Welcome {user_name}!**\n\n"
        "🤖 **Ultra Terabox Bot**\n"
        "📥 Send me a Terabox link to download files!\n\n"
        "🔧 **Bot is running in simple mode**\n"
        "Send any Terabox URL to start downloading!",
        parse_mode='Markdown'
    )

async def simple_test(update, context):
    """Simple test command"""
    await update.message.reply_text("✅ **Bot is working!**\n\n🤖 All systems operational!")

async def simple_message_handler(update, context):
    """Simple message handler"""
    user_id = update.effective_user.id
    message_text = update.message.text
    
    LOGGER.info(f"📨 Message from {user_id}: {message_text}")
    
    # Basic Terabox detection
    terabox_domains = ['terabox.com', '1024tera.com', 'nephobox.com', 'mirrobox.com', 'momerybox.com']
    is_terabox_url = any(domain in message_text.lower() for domain in terabox_domains)
    
    if is_terabox_url:
        await update.message.reply_text(
            "🎯 **Terabox URL Detected!**\n\n"
            "🔧 Processing system is loading...\n"
            "⏰ Please wait while we set up the download system.",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            f"📢 **Echo:** {message_text}\n\n"
            f"🆔 **Your ID:** `{user_id}`\n"
            f"🤖 **Bot is working!**\n\n"
            f"Send a Terabox URL to download!",
            parse_mode='Markdown'
        )

async def main():
    """Main function - FIXED VERSION"""
    try:
        LOGGER.info("🚀 Starting Ultra Terabox Bot (Fixed Version)...")
        
        # Create application
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Store start time for uptime
        import time
        application.start_time = time.time()

        # Clear webhooks first
        try:
            LOGGER.info("🧹 Clearing webhooks...")
            await application.bot.delete_webhook(drop_pending_updates=True)
            LOGGER.info("✅ Webhooks cleared")
        except Exception as e:
            LOGGER.warning(f"⚠️ Webhook clear failed: {e}")

        # Set up bot menu
        await setup_bot_commands(application)

        # Add handlers based on availability
        if commands_available:
            LOGGER.info("✅ Using enhanced command handlers")
            application.add_handler(CommandHandler("start", commands.start))
            try:
                application.add_handler(CommandHandler("help", commands.help_command))
                application.add_handler(CommandHandler("contact", commands.contact_command))
                application.add_handler(CommandHandler("about", commands.about_command))
                application.add_handler(CommandHandler("status", commands.status_command))
            except AttributeError:
                LOGGER.warning("Some enhanced commands not available, using fallbacks")
            
            try:
                application.add_handler(CommandHandler("test", commands.test_handler))
            except AttributeError:
                application.add_handler(CommandHandler("test", simple_test))
            
            try:
                application.add_handler(CommandHandler("leech", commands.leech_command))
            except AttributeError:
                LOGGER.warning("Leech command not available")
        else:
            LOGGER.info("🔧 Using simple fallback handlers")
            application.add_handler(CommandHandler("start", simple_start))
            application.add_handler(CommandHandler("test", simple_test))

        # Add message handler
        if messages_available:
            LOGGER.info("✅ Using enhanced message handler")
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, messages.handle_message))
        else:
            LOGGER.info("🔧 Using simple message handler")
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, simple_message_handler))

        # ✅ FIXED: Try to add verification callbacks safely
        try:
            from bot.modules.token_verification import handle_verification_callbacks
            application.add_handler(CallbackQueryHandler(handle_verification_callbacks))
            LOGGER.info("✅ Verification callbacks registered")
        except ImportError:
            LOGGER.info("ℹ️ Verification system not available")
        except Exception as e:
            LOGGER.warning(f"⚠️ Verification callback setup failed: {e}")

        # Log startup info
        LOGGER.info("✅ All available handlers registered")
        LOGGER.info(f"🤖 Bot Token: {BOT_TOKEN[:20]}...")
        LOGGER.info(f"👤 Owner ID: {OWNER_ID}")
        LOGGER.info("🟢 Bot starting...")

        # ✅ FIXED: Start polling with proper error handling
        LOGGER.info("🎯 Starting bot polling...")
        await application.run_polling(
            drop_pending_updates=True,
            allowed_updates=["message", "callback_query"]
        )
        
    except Exception as e:
        LOGGER.error(f"❌ Error in main: {e}")
        raise

def run_bot():
    """Entry point with proper async handling"""
    import asyncio
    
    # ✅ FIXED: Handle existing event loops properly
    try:
        # Try to get existing loop
        loop = asyncio.get_running_loop()
        LOGGER.info("📍 Detected existing event loop, creating task")
        
        # Create a new task in the existing loop
        task = loop.create_task(main())
        
        # Keep the task running
        def keep_alive():
            if not task.done():
                loop.call_later(1.0, keep_alive)
        
        keep_alive()
        return task
        
    except RuntimeError:
        # No existing loop, run normally
        LOGGER.info("🚀 Starting new event loop")
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            LOGGER.info("👋 Bot stopped by user")
        except Exception as e:
            LOGGER.error(f"❌ Fatal error: {e}")

if __name__ == "__main__":
    run_bot()
                
