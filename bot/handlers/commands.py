"""
Bot command handlers - WITH ENHANCED MODE OPTION
"""

from telegram import Update
from telegram.ext import ContextTypes
from config import LOGGER, OWNER_ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start command handler"""
    user_id = update.effective_user.id
    LOGGER.info(f"Start command from user {user_id}")
    
    text = f"""
🚀 **Ultra Terabox Leech Bot - Enhanced Edition**

**Commands:**
• `/leech <url>` - Standard speed leech
• `/fast <url>` - Enhanced multi-connection leech
• `/test` - Test bot functionality

**Supported:**
• terabox.com • teraboxurl.com • 1024tera.com

**Features:**
• ⚡ Multi-connection downloads (Enhanced mode)
• 🔄 Automatic fallback to simple mode
• 🔄 Retry logic with exponential backoff
• 💾 Memory optimized streaming
• 🆓 Free tier friendly

**Modes:**
• **Standard Mode:** Reliable, slower speed
• **Enhanced Mode:** Multiple connections, faster speed

**Your ID:** `{user_id}` | **Owner:** `{OWNER_ID}`

Send a Terabox link or use commands! 📂
    """
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def test_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Test command"""
    await update.message.reply_text("🧪 **Enhanced Bot Status: ✅ WORKING!**", parse_mode='Markdown')

async def leech_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Standard leech command"""
    user_id = update.effective_user.id
    LOGGER.info(f"Standard leech command from user {user_id}")
    
    if not context.args:
        await update.message.reply_text("❌ **Usage:** `/leech <terabox_url>`", parse_mode='Markdown')
        return
    
    from .processor import process_terabox_url
    url = context.args[0]
    await process_terabox_url(update, url)

async def fast_leech_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Enhanced fast leech command"""
    user_id = update.effective_user.id
    LOGGER.info(f"Enhanced leech command from user {user_id}")
    
    if not context.args:
        await update.message.reply_text("❌ **Usage:** `/fast <terabox_url>`", parse_mode='Markdown')
        return
    
    try:
        from .enhanced_processor import enhanced_process_terabox_url
        url = context.args[0]
        await enhanced_process_terabox_url(update, url)
    except ImportError:
        await update.message.reply_text("❌ **Enhanced mode not available. Using standard mode...**", parse_mode='Markdown')
        from .processor import process_terabox_url
        url = context.args[0]
        await process_terabox_url(update, url)
        
