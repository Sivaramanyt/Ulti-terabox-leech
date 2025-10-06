"""
Ultra Simple Terabox Leech Bot
No complex imports, no wrappers, just pure functionality
"""

from pyrogram import Client, idle, filters
from pyrogram.types import Message
from config import BOT_TOKEN, TELEGRAM_API, TELEGRAM_HASH, LOGGER, DOWNLOAD_DIR
import asyncio
import aiohttp
import aiofiles
from pathlib import Path
import os

# Create bot client
app = Client(
    "terabox_bot",
    api_id=TELEGRAM_API,
    api_hash=TELEGRAM_HASH,
    bot_token=BOT_TOKEN
)

# Import only the terabox function
try:
    from .helper.mirror_leech_utils.download_utils.direct_link_generator import terabox
except:
    # Fallback if import fails
    def terabox(url):
        raise Exception("Terabox function not available")

@app.on_message(filters.command("start"))
async def start_handler(client, message: Message):
    """Start command"""
    await message.reply_text("""
🚀 **Ultra Simple Terabox Leech Bot**

**Commands:**
• `/leech <terabox_url>` - Download from Terabox
• Just send Terabox URL directly

**Features:**
• ⚡ Lightning fast
• 🎯 Terabox only  
• 💾 Memory optimized
• 🆓 Free tier friendly
    """)

@app.on_message(filters.command("leech"))
async def leech_command(client, message: Message):
    """Leech command handler"""
    if len(message.command) < 2:
        await message.reply_text("❌ **Usage:** `/leech https://terabox.com/s/xxxxx`")
        return
    
    url = message.command[1]
    await download_and_upload(message, url)

@app.on_message(filters.regex(r"terabox\.com") & filters.text & ~filters.command(["start", "leech"]))
async def auto_leech(client, message: Message):
    """Auto-detect Terabox URLs"""
    await download_and_upload(message, message.text.strip())

async def download_and_upload(message: Message, url: str):
    """Main download and upload function"""
    status = await message.reply_text("🔍 **Processing...**")
    
    try:
        # Get file info from Terabox
        await status.edit_text("📋 **Getting file info...**")
        file_info = terabox(url)
        
        if file_info['type'] != 'file':
            await status.edit_text("❌ **Only single files supported**")
            return
        
        filename = file_info['filename']
        file_size = file_info['size']
        download_url = file_info['download_url']
        
        # Size check (2GB limit)
        if file_size > 2 * 1024 * 1024 * 1024:
            await status.edit_text("❌ **File too large! Max: 2GB**")
            return
        
        await status.edit_text(f"📁 **{filename}**\n📊 **{format_size(file_size)}**\n⬇️ **Downloading...**")
        
        # Download file
        file_path = Path(DOWNLOAD_DIR) / filename
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        
        async with aiohttp.ClientSession() as session:
            async with session.get(download_url) as response:
                if response.status != 200:
                    await status.edit_text(f"❌ **Download failed: HTTP {response.status}**")
                    return
                
                async with aiofiles.open(file_path, 'wb') as f:
                    async for chunk in response.content.iter_chunked(8192):
                        await f.write(chunk)
        
        # Upload to Telegram
        await status.edit_text(f"📤 **Uploading...**")
        
        try:
            # Detect file type and upload accordingly
            if filename.lower().endswith(('.mp4', '.avi', '.mkv', '.mov', '.wmv')):
                await message.reply_video(
                    video=str(file_path),
                    caption=f"🎥 **{filename}**"
                )
            elif filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                await message.reply_photo(
                    photo=str(file_path),
                    caption=f"🖼️ **{filename}**"
                )
            else:
                await message.reply_document(
                    document=str(file_path),
                    caption=f"📁 **{filename}**"
                )
            
            # Success - delete status message
            await status.delete()
            
        except Exception as upload_error:
            await status.edit_text(f"❌ **Upload failed:** {str(upload_error)}")
        
        # Cleanup downloaded file
        try:
            file_path.unlink(missing_ok=True)
        except:
            pass
            
    except Exception as e:
        LOGGER.error(f"Process error: {e}")
        await status.edit_text(f"❌ **Error:** {str(e)}")

def format_size(bytes):
    """Format file size"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024:
            return f"{bytes:.1f} {unit}"
        bytes /= 1024
    return f"{bytes:.1f} TB"

async def main():
    """Main function"""
    try:
        await app.start()
        me = await app.get_me()
        LOGGER.info(f"✅ Bot @{me.username} started successfully!")
        await idle()
    except Exception as e:
        LOGGER.error(f"❌ Bot startup error: {e}")
    finally:
        await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
    
