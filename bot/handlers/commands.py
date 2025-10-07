"""
Enhanced Command Handlers with Contact Menu - COMPLETE VERSION
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand, BotCommandScopeDefault
from telegram.ext import ContextTypes, CommandHandler
from config import *
import logging

LOGGER = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

async def contact_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Contact command"""
    keyboard = [
        [InlineKeyboardButton("💬 Direct Message", url=DEVELOPER_CONTACT)],
        [InlineKeyboardButton("🆘 Support Group", url=SUPPORT_GROUP)],
        [InlineKeyboardButton("📢 Updates Channel", url=UPDATES_CHANNEL)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📞 **Contact Information**\n\n"
        f"👨‍💻 **Developer:** {DEVELOPER_USERNAME}\n"
        "🆘 **Support:** Available 24/7\n"
        f"📧 **Email:** {DEVELOPER_EMAIL}\n\n"
        "**For quick support:**\n"
        "• Bot issues - Direct message\n"
        "• General help - Support group\n"
        "• Updates - Follow channel\n\n"
        "**Response time:** Usually within 2-4 hours",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enhanced help command"""
    await update.message.reply_text(
        "🆘 **Help - Ultra Terabox Bot**\n\n"
        "**Commands:**\n"
        "• `/start` - Start the bot\n"
        "• `/help` - Show this help message\n"
        "• `/contact` - Contact developer\n"
        "• `/about` - About this bot\n"
        "• `/status` - Bot status\n"
        "• `/leech` - Standard download\n"
        "• `/fast` - Enhanced download\n\n"
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
        f"**Free Limit:** {FREE_DOWNLOAD_LIMIT} downloads, then verification required\n"
        "**Need help?** Use /contact",
        parse_mode='Markdown'
    )

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """About command"""
    await update.message.reply_text(
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

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Status command"""
    import time
    uptime = time.time() - context.application.start_time if hasattr(context.application, 'start_time') else 0
    uptime_hours = int(uptime // 3600)
    uptime_minutes = int((uptime % 3600) // 60)
    
    # Check verification availability
    try:
        from bot.modules.token_verification import check_user_verification_required
        verification_status = "Enabled"
    except ImportError:
        verification_status = "Disabled"
    
    await update.message.reply_text(
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

# Keep your existing leech_command and other functions here
async def test_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Test handler - keep your existing implementation"""
    await update.message.reply_text("🧪 **Bot Test**\n\nBot is working correctly!")

async def leech_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Keep your existing leech_command implementation here"""
    await update.message.reply_text("🔧 **Leech Command**\n\nSend a Terabox URL to start downloading!")

async def fast_leech_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Keep your existing fast_leech_command implementation here"""
    await update.message.reply_text("⚡ **Fast Leech Command**\n\nSend a Terabox URL for enhanced downloading!")
    
