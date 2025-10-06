from pyrogram import filters
from pyrogram.types import Message
from ..core.tg_client import TgClient
from ..helper.mirror_leech_utils.download_utils.direct_link_generator import terabox
from ..helper.mirror_leech_utils.download_utils.direct_downloader import DirectDownloader
from ..helper.mirror_leech_utils.upload_utils.telegram_uploader import TelegramUploader
from ..helper.telegram_helper.message_utils import sendMessage, editMessage
from ..helper.ext_utils.bot_utils import new_task
from config import LOGGER, OWNER_ID, AUTHORIZED_CHATS

@TgClient.bot.on_message(filters.command("start"))
async def start_handler(client, message: Message):
    """Start command handler"""
    text = """
🚀 **Professional Terabox Leech Bot**

Send me a Terabox link to download and upload to Telegram!

**Commands:**
• `/leech <terabox_url>` - Download from Terabox
• Just send Terabox URL directly

**Features:**
• Fast downloads from Terabox
• Auto file splitting for large files
• Progress tracking
• Memory optimized for free hosting

**Supported:** Videos, Documents, Images, Archives
    """
    await sendMessage(message, text)

@TgClient.bot.on_message(filters.command("leech"))
@new_task
async def leech_handler(client, message: Message):
    """Leech command handler"""
    if len(message.command) < 2:
        await sendMessage(message, "❌ Please provide a Terabox URL\n\nExample: `/leech https://terabox.com/s/xxxxx`")
        return
    
    url = message.command[1]
    await process_terabox_leech(message, url)

@TgClient.bot.on_message(filters.regex(r"terabox\.com") & filters.text)
@new_task
async def auto_leech_handler(client, message: Message):
    """Auto leech when Terabox URL is detected"""
    url = message.text.strip()
    await process_terabox_leech(message, url)

async def process_terabox_leech(message: Message, url: str):
    """Process Terabox leech request"""
    status_msg = await sendMessage(message, "🔍 **Processing Terabox URL...**")
    
    try:
        # Get file information
        await editMessage(status_msg, "📋 **Getting file information...**")
        file_info = terabox(url)
        
        if file_info['type'] == 'file':
            # Single file
            filename = file_info['filename']
            file_size = file_info['size']
            download_url = file_info['download_url']
            
            # Check file size (2GB limit for free tier)
            if file_size > 2 * 1024 * 1024 * 1024:
                await editMessage(status_msg, "❌ **File too large!** Maximum size: 2GB for free tier")
                return
            
            await editMessage(status_msg, f"📁 **File:** `{filename}`\n📊 **Size:** `{format_size(file_size)}`\n⬇️ **Downloading...**")
            
            # Download file
            downloader = DirectDownloader()
            file_path = await downloader.download_file(download_url, filename, message, status_msg)
            
            if file_path:
                # Upload to Telegram
                await editMessage(status_msg, f"📤 **Uploading to Telegram...**")
                uploader = TelegramUploader()
                await uploader.upload_file(file_path, message, status_msg)
                
                # Cleanup
                import os
                if os.path.exists(file_path):
                    os.remove(file_path)
                
                await status_msg.delete()
            
        else:
            await editMessage(status_msg, "❌ **Folder downloads not supported in this version**")
            
    except Exception as e:
        LOGGER.error(f"Leech error: {e}")
        await editMessage(status_msg, f"❌ **Error:** {str(e)}")

def format_size(size_bytes):
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"
