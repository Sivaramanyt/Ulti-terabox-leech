"""
Ultra Simple Terabox Leech Bot - FIXED EVENT LOOP VERSION
"""

import asyncio
import logging
import time
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from telegram import BotCommand, BotCommandScopeDefault
from config import BOT_TOKEN, LOGGER

import bot.utils.health_server as health
import bot.handlers.commands as commands
import bot.handlers.messages as messages

# Import callback handlers
try:
    from bot.handlers.callbacks import setup_callback_handlers
    callbacks_available = True
except ImportError:
    callbacks_available = False

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def setup_bot_commands(application):
    """Set up bot menu commands"""
    commands_list = [
        BotCommand("start", "🏠 Start the bot"),
        BotCommand("help", "🆘 Get help"),
        BotCommand("contact", "📞 Contact developer"),
        BotCommand("about", "ℹ️ About this bot"),
        BotCommand("status", "📊 Bot status"),
        BotCommand("leech", "📥 Standard download"),
        BotCommand("fast", "⚡ Enhanced download")
    ]
    
    await application.bot.set_my_commands(commands_list, scope=BotCommandScopeDefault())
    LOGGER.info("✅ Bot menu commands set successfully")

async def main():
    """Main function with FIXED event loop handling"""
    try:
        # Start health check server first
        await health.start_health_server()

        # Create application
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Store start time for uptime calculation
        application.start_time = time.time()

        # Clear webhooks
        LOGGER.info("🧹 Clearing any existing webhooks...")
        await application.bot.delete_webhook(drop_pending_updates=True)
        LOGGER.info("✅ Webhook cleared successfully")
        await asyncio.sleep(3)

        # Set up bot menu commands
        await setup_bot_commands(application)

        # Add enhanced command handlers
        application.add_handler(CommandHandler("start", commands.start))
        application.add_handler(CommandHandler("help", commands.help_command))
        application.add_handler(CommandHandler("contact", commands.contact_command))
        application.add_handler(CommandHandler("about", commands.about_command))
        application.add_handler(CommandHandler("status", commands.status_command))
        application.add_handler(CommandHandler("test", commands.test_handler))
        
        # Standard leech command
        application.add_handler(CommandHandler("leech", commands.leech_command))

        # Enhanced fast leech command
        try:
            import bot.handlers.enhanced_processor
            application.add_handler(CommandHandler("fast", commands.fast_leech_command))
            LOGGER.info("Enhanced multi-connection mode available")
            enhanced_available = True
        except ImportError as e:
            LOGGER.warning(f"Enhanced mode not available: {e}")
            application.add_handler(CommandHandler("fast", commands.leech_command))
            enhanced_available = False

        # Setup callback handlers if available
        if callbacks_available:
            setup_callback_handlers(application)
            LOGGER.info("✅ Callback handlers registered")

        # ✅ FIXED: Try to handle verification callbacks properly
        try:
            from bot.modules.token_verification import handle_verification_callbacks as orig_verify_handler
            
            # Create a combined callback handler
            async def combined_callback_handler(update, context):
                query = update.callback_query
                if query.data in ["about", "status", "why_verify"] or query.data.startswith("start_verification"):
                    if callbacks_available:
                        await handle_callback_queries(update, context)
                    else:
                        await query.answer("Feature not available")
                else:
                    await orig_verify_handler(update, context)
            
            application.add_handler(CallbackQueryHandler(combined_callback_handler))
            LOGGER.info("✅ Combined verification callback handler registered")
        except Exception as e:
            LOGGER.error(f"❌ Failed to register verification handlers: {e}")
            if callbacks_available:
                setup_callback_handlers(application)

        # Message handler for direct URL processing
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, messages.handle_message))

        LOGGER.info("✅ All handlers registered")
        LOGGER.info(f"🤖 Bot Token: {BOT_TOKEN[:20]}...")
        LOGGER.info(f"👤 Owner ID: 1206988513")
        LOGGER.info("🔐 Verification: ENABLED")
        LOGGER.info("🟢 Bot starting...")
        LOGGER.info("🎯 Ready to process Terabox links!")

        # ✅ FIXED: Start the bot with proper event loop handling
        try:
            # Use run_polling instead of manual start/stop
            await application.run_polling(
                drop_pending_updates=True,
                allowed_updates=["message", "callback_query"],
                close_loop=False  # ✅ CRITICAL FIX: Don't close the event loop
            )
        except Exception as polling_error:
            LOGGER.error(f"❌ Polling error: {polling_error}")
            # Don't re-raise, just log and continue
            
    except Exception as e:
        LOGGER.error(f"❌ Error in main: {e}")
        # Don't exit immediately, try fallback
        await basic_bot_fallback()

async def basic_bot_fallback():
    """Basic fallback bot if main bot fails"""
    try:
        LOGGER.info("🔄 Starting in BASIC FALLBACK mode...")
        application = Application.builder().token(BOT_TOKEN).build()

        # Store start time
        application.start_time = time.time()

        # Only add essential handlers
        application.add_handler(CommandHandler("start", commands.start))
        application.add_handler(CommandHandler("help", commands.help_command))
        application.add_handler(CommandHandler("contact", commands.contact_command))
        application.add_handler(CommandHandler("test", commands.test_handler))
        application.add_handler(CommandHandler("leech", commands.leech_command))
        application.add_handler(CommandHandler("fast", commands.leech_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, messages.handle_message))

        LOGGER.info("✅ BASIC BOT: Running in safe fallback mode")

        # ✅ FIXED: Proper fallback polling
        await application.run_polling(
            drop_pending_updates=True,
            allowed_updates=["message", "callback_query"],
            close_loop=False
        )
        
    except Exception as e:
        LOGGER.error(f"❌ FALLBACK ERROR: {e}")

# ✅ FIXED: Proper event loop handling
def run_bot():
    """Run bot with proper event loop management"""
    try:
        # Check if there's already a running event loop
        try:
            loop = asyncio.get_running_loop()
            LOGGER.warning("Event loop already running, creating new task")
            # If we're in an existing loop, create a task
            task = loop.create_task(main())
            return task
        except RuntimeError:
            # No running loop, we can run normally
            return asyncio.run(main())
    except KeyboardInterrupt:
        LOGGER.info("👋 Bot stopped by user")
    except Exception as e:
        LOGGER.error(f"❌ FATAL ERROR: {e}")

if __name__ == "__main__":
    run_bot()
    
