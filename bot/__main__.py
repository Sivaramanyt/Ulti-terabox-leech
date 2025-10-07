"""
Ultra Simple Terabox Leech Bot - Enhanced Edition with Contact Menu + Fixed Verification
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
    """Main function with enhanced features"""
    try:
        # Start health check server
        await health.start_health_server()

        # Create application
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Store start time for uptime calculation
        application.start_time = time.time()

        # Set up bot menu commands
        await setup_bot_commands(application)

        # Add enhanced command handlers
        application.add_handler(CommandHandler("start", commands.start))
        application.add_handler(CommandHandler("help", commands.help_command))
        application.add_handler(CommandHandler("contact", commands.contact_command))
        application.add_handler(CommandHandler("about", commands.about_command))
        application.add_handler(CommandHandler("status", commands.status_command))
        application.add_handler(CommandHandler("test", commands.test_handler))
        
        # Standard leech command (your reliable working version)
        application.add_handler(CommandHandler("leech", commands.leech_command))

        # Enhanced fast leech command (new multi-connection mode)
        try:
            # Try to import enhanced mode
            import bot.handlers.enhanced_processor
            application.add_handler(CommandHandler("fast", commands.fast_leech_command))
            print("✅ Enhanced mode loaded successfully")
            LOGGER.info("Enhanced multi-connection mode available")
            enhanced_available = True
        except ImportError as e:
            print(f"⚠️ Enhanced mode not available: {e}")
            LOGGER.warning(f"Enhanced mode not available: {e}")
            # Add fallback - /fast will use standard mode
            application.add_handler(CommandHandler("fast", commands.leech_command))
            enhanced_available = False

        # Setup callback handlers if available
        if callbacks_available:
            setup_callback_handlers(application)
            LOGGER.info("✅ Callback handlers registered")

        # Message handler for direct URL processing (uses enhanced verification)
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, messages.handle_message))

        # Bot startup messages
        print(f"🚀 Bot starting with token: {BOT_TOKEN[:20]}...")
        print(f"🌐 Health check server running on port 8000")
        print(f"🔍 DEBUG MODE: All messages will be logged")
        print(f"📞 CONTACT MENU: Professional contact system enabled")
        print(f"🔐 VERIFICATION: Enhanced verification system with retry logic")
        
        if enhanced_available:
            print(f"⚡ ENHANCED MODE: Multi-connection downloads available")
            print(f"📋 COMMANDS: /leech (standard) | /fast (enhanced)")
        else:
            print(f"🔧 STANDARD MODE: Reliable single-connection downloads")
            print(f"📋 COMMANDS: /leech (standard) | /fast (fallback to standard)")

        # Start the bot
        await application.initialize()
        await application.start()
        await application.updater.start_polling()

        if enhanced_available:
            LOGGER.info("✅ Bot started successfully with Enhanced Multi-Connection Mode + Contact Menu!")
            print("✅ Bot is now running with ENHANCED Terabox processing + Professional Contact Menu!")
            print("🚀 Use /fast for high-speed multi-connection downloads")
            print("🛡️ Use /leech for reliable standard downloads")
        else:
            LOGGER.info("✅ Bot started successfully with Standard Mode + Contact Menu!")
            print("✅ Bot is now running with STANDARD Terabox processing + Professional Contact Menu!")
            print("🔧 Both /leech and /fast use reliable standard mode")

        print("\n" + "="*60)
        print("📋 AVAILABLE COMMANDS:")
        print("• /start - Show bot information with contact menu")
        print("• /contact - Professional contact information")
        print("• /help - Comprehensive help system")
        print("• /about - About the bot")
        print("• /status - Real-time bot status")
        print("• /test - Test bot functionality")
        print("• /leech - Standard reliable download")
        if enhanced_available:
            print("• /fast - Enhanced multi-connection download (NEW)")
        else:
            print("• /fast - Fallback to standard download")
        print("• Direct URL - Send Terabox URL for processing with verification")
        print("="*60 + "\n")

        # Keep running
        while True:
            await asyncio.sleep(1)

    except Exception as e:
        LOGGER.error(f"❌ Bot startup error: {e}")
        print(f"❌ ERROR: {e}")
        print("🔄 Falling back to basic bot mode...")

        # Fallback mode - basic bot without enhanced features
        try:
            await basic_bot_fallback()
        except Exception as fallback_error:
            LOGGER.error(f"❌ Fallback mode also failed: {fallback_error}")
            print(f"❌ CRITICAL ERROR: {fallback_error}")

async def basic_bot_fallback():
    """Basic fallback bot if enhanced mode completely fails"""
    print("🔄 Starting in BASIC FALLBACK mode...")
    application = Application.builder().token(BOT_TOKEN).build()

    # Only add essential handlers
    application.add_handler(CommandHandler("start", commands.start))
    application.add_handler(CommandHandler("help", commands.help_command))
    application.add_handler(CommandHandler("contact", commands.contact_command))
    application.add_handler(CommandHandler("test", commands.test_handler))
    application.add_handler(CommandHandler("leech", commands.leech_command))
    application.add_handler(CommandHandler("fast", commands.leech_command))  # Fast fallback to standard
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, messages.handle_message))

    print("✅ BASIC BOT: Running in safe fallback mode with contact menu")
    LOGGER.info("Basic fallback mode activated")

    await application.initialize()
    await application.start()
    await application.updater.start_polling()

    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
        LOGGER.info("Bot stopped by user")
    except Exception as e:
        print(f"❌ FATAL ERROR: {e}")
        LOGGER.error(f"Fatal error: {e}")
    
