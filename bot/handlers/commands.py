"""
Bot command handlers
"""

from telegram import Update
from telegram.ext import ContextTypes
from config import LOGGER, OWNER_ID
from .processor import process_terabox_url

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start command handler"""
    user_id = update.effective_user.id
    LOGGER.info(f"Start command from user {user_id}")
    print(f"🚀 DEBUG: Start command received from {user_id}")
    
    text = f"""
🚀 **Ultra Simple Terabox Leech Bot**

**Usage:**
• `/leech <terabox_url>`
• Just send Terabox URL directly

**Supported Sites:**
• 🔗 terabox.com
• 🔗 teraboxurl.com  
• 🔗 terasharelink.com
• 🔗 1024tera.com
• 🔗 momerybox.com

**Features:**
• ⚡ Lightning fast downloads
• 🎯 Multiple Terabox domains
• 💾 Memory optimized
• 🆓 Free tier friendly

**Debug Info:**
• Your ID: `{user_id}`
• Owner ID: `{OWNER_ID}`
• Bot Status: ✅ WORKING

Send me a supported link to get started! 📂
    """
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def test_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Test command"""
    await update.message.reply_text("🧪 **Test successful!** Bot is responding to commands!", parse_mode='Markdown')

async def leech_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Leech command handler"""
    user_id = update.effective_user.id
    LOGGER.info(f"Leech command from user {user_id}")
    print(f"📥 DEBUG: Leech command from {user_id}")
    
    if not context.args:
        await update.message.reply_text(
            "❌ **Usage:** `/leech <url>`\n\n**Supported:**\n• terabox.com\n• teraboxurl.com\n• terasharelink.com", 
            parse_mode='Markdown'
        )
        return
    
    url = context.args[0]
    await process_terabox_url(update, url)
