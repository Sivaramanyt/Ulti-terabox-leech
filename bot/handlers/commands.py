
"""
Bot command handlers - FIXED FUNCTIONS
"""

from telegram import Update
from telegram.ext import ContextTypes
from config import LOGGER, OWNER_ID

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

**Supported:**
• terabox.com • teraboxurl.com • 1024tera.com

**Features:**
• ⚡ Lightning fast • 🎯 Uses wdzone-terabox-api
• 💾 Memory optimized • 🆓 Free tier friendly

**Debug Info:**
• Your ID: `{user_id}` • Owner ID: `{OWNER_ID}`
• Bot Status: ✅ WORKING

Send me a Terabox link! 📂
    """
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def test_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Test command"""
    await update.message.reply_text("🧪 **Test successful!** Bot working!", parse_mode='Markdown')

async def leech_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Leech command handler"""
    user_id = update.effective_user.id
    LOGGER.info(f"Leech command from user {user_id}")
    print(f"📥 DEBUG: Leech command from {user_id}")
    
    if not context.args:
        await update.message.reply_text("❌ **Usage:** `/leech <terabox_url>`", parse_mode='Markdown')
        return
    
    # Import here to avoid circular imports
    from bot.handlers.processor import process_terabox_url
    url = context.args[0]
    await process_terabox_url(update, url)
