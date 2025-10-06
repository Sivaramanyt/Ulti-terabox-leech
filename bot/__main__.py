from pyrogram import Client, idle, filters
from pyrogram.types import Message
from config import BOT_TOKEN, TELEGRAM_API, TELEGRAM_HASH, LOGGER
import asyncio

# Create the bot client directly
app = Client(
    "terabox_bot",
    api_id=TELEGRAM_API,
    api_hash=TELEGRAM_HASH,
    bot_token=BOT_TOKEN
)

# Import utilities
from .helper.mirror_leech_utils.download_utils.direct_link_generator import terabox
from .helper.telegram_helper.message_utils import sendMessage, editMessage

@app.on_message(filters.command("start"))
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
• Progress tracking
• Memory optimized for free hosting

**Supported:** Videos, Documents, Images, Archives
    """
    await message.reply_text(text)

@app.on_message(filters.command("leech"))
async def leech_handler(client, message: Message):
    """Leech command handler"""
    if len(message.command) < 2:
        await message.reply_text("❌ Please provide a Terabox URL\n\nExample: `/leech https://terabox.com/s/xxxxx`")
        return
    
    url = message.command[1]
    await process_terabox_leech(message, url)

@app.on_message(filters.regex(r"terabox\.com") & filters.text)
async def auto_leech_handler(client, message: Message):
    """Auto leech when Terabox URL is detected"""
    url = message.text.strip()
    await process_terabox_leech(message, url)

async def process_terabox_leech(message: Message, url: str):
    """Process Terabox leech request"""
    status_msg = await message.reply_text("🔍 **Processing Terabox URL...**")
    
    try:
        # Get file information
        await status_msg.edit_text("📋 **Getting file information...**")
        file_info = terabox(url)
        
        if file_info['type'] == 'file':
            filename = file_info['filename']
            file_size = file_info['size']
            download_url = file_info['download_url']
            
            # Check file size (2GB limit)
            if file_size > 2 * 1024 * 1024 * 1024:
                await status_msg.edit_text("❌ **File too large!** Maximum size: 2GB")
                return
            
            await status_msg.edit_text(
                f"📁 **File:** `{filename}`\n"
                f"📊 **Size:** `{format_size(file_size)}`\n"
                f"⬇️ **Starting download...**"
            )
            
            # Simple download and upload
            import aiohttp
            import aiofiles
            from pathlib import Path
            from config import DOWNLOAD_DIR
            
            # Download
            file_path = Path(DOWNLOAD_DIR) / filename
            async with aiohttp.ClientSession() as session:
                async with session.get(download_url) as response:
                    if response.status == 200:
                        async with aiofiles.open(file_path, 'wb') as f:
                            async for chunk in response.content.iter_chunked(8192):
                                await f.write(chunk)
            
            # Upload to Telegram
            await status_msg.edit_text("📤 **Uploading to Telegram...**")
            
            if filename.lower().endswith(('.mp4', '.avi', '.mkv', '.mov')):
                await message.reply_video(
                    video=str(file_path),
                    caption=f"🎥 **{filename}**"
                )
            else:
                await message.reply_document(
                    document=str(file_path),
                    caption=f"📁 **{filename}**"
                )
            
            # Cleanup
            file_path.unlink(missing_ok=True)
            await status_msg.delete()
            
        else:
            await status_msg.edit_text("❌ **Folder downloads not supported**")
            
    except Exception as e:
        LOGGER.error(f"Leech error: {e}")
        await status_msg.edit_text(f"❌ **Error:** {str(e)}")

def format_size(size_bytes):
    """Format file size"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

async def main():
    """Main function"""
    try:
        await app.start()
        LOGGER.info("✅ Terabox Leech Bot started successfully!")
        await idle()
    except Exception as e:
        LOGGER.error(f"Bot error: {e}")
    finally:
        await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
