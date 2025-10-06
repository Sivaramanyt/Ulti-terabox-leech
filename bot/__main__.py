"""
Ultra Simple Terabox Leech Bot - WITH HEALTH CHECK
Fixed Koyeb health check issue
"""

from pyrogram import Client, idle, filters
from pyrogram.types import Message
from config import BOT_TOKEN, TELEGRAM_API, TELEGRAM_HASH, LOGGER, DOWNLOAD_DIR
import asyncio
import aiohttp
import aiofiles
from pathlib import Path
import os
from aiohttp import web

# Create bot client
app = Client(
    f"terabox_bot_{BOT_TOKEN.split(':')[0]}",
    api_id=TELEGRAM_API,
    api_hash=TELEGRAM_HASH,
    bot_token=BOT_TOKEN
)

# Health check server for Koyeb
async def health_check(request):
    return web.Response(text="Bot is running!", status=200)

async def start_health_server():
    """Start health check server for Koyeb"""
    app_web = web.Application()
    app_web.router.add_get('/', health_check)
    app_web.router.add_get('/health', health_check)
    
    runner = web.AppRunner(app_web)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8000)
    await site.start()
    LOGGER.info("Health check server started on port 8000")

# Your existing Terabox function
def extract_terabox_info(url):
    """Extract file info from Terabox URL"""
    import requests
    from urllib.parse import urlparse, parse_qs
    
    try:
        # Extract surl from URL
        if 'surl=' in url:
            surl = url.split('surl=')[-1].split('&')[0]
        elif '/s/' in url:
            surl = url.split('/s/')[-1].split('?')[0]
        else:
            raise Exception("Invalid Terabox URL")
        
        # API request
        api_url = "https://www.terabox.com/api/shorturlinfo"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        params = {'shorturl': surl, 'root': '1'}
        
        response = requests.get(api_url, params=params, headers=headers, timeout=30)
        data = response.json()
        
        if data.get('errno') != 0:
            raise Exception(f"API Error: {data.get('errmsg', 'Unknown error')}")
        
        files = data.get('list', [])
        if not files:
            raise Exception("No files found")
        
        file_info = files[0]
        return {
            'filename': file_info.get('server_filename', 'Unknown'),
            'size': file_info.get('size', 0),
            'download_url': file_info.get('dlink', ''),
            'type': 'file'
        }
        
    except Exception as e:
        raise Exception(f"Terabox extraction failed: {str(e)}")

# Your existing handlers (keep all of them the same)
@app.on_message(filters.command("start"))
async def start_handler(client, message: Message):
    """Start command"""
    await message.reply_text("""
🚀 **Ultra Simple Terabox Leech Bot**

**Usage:**
• `/leech <terabox_url>`
• Just send Terabox URL directly

**Features:**
• ⚡ Lightning fast
• 🎯 Terabox only  
• 💾 Memory optimized
• 🆓 Free tier friendly (512MB RAM)

Send me a Terabox link to get started! 📂
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
    status = await message.reply_text("🔍 **Processing Terabox URL...**")
    
    try:
        # Get file info from Terabox
        await status.edit_text("📋 **Extracting file info...**")
        file_info = extract_terabox_info(url)
        
        filename = file_info['filename']
        file_size = file_info['size']
        download_url = file_info['download_url']
        
        if not download_url:
            await status.edit_text("❌ **No download URL found**")
            return
        
        # Size check (2GB limit for free tier)
        if file_size > 2 * 1024 * 1024 * 1024:
            await status.edit_text("❌ **File too large!** Max: 2GB for free tier")
            return
        
        await status.edit_text(
            f"📁 **{filename}**\n"
            f"📊 **{format_size(file_size)}**\n"
            f"⬇️ **Downloading...**"
        )
        
        # Download file
        file_path = Path(DOWNLOAD_DIR) / filename
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        
        async with aiohttp.ClientSession() as session:
            async with session.get(download_url) as response:
                if response.status != 200:
                    await status.edit_text(f"❌ **Download failed: HTTP {response.status}**")
                    return
                
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                async with aiofiles.open(file_path, 'wb') as f:
                    async for chunk in response.content.iter_chunked(8192):
                        await f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Update progress every 1MB
                        if downloaded % (1024 * 1024) == 0 and total_size > 0:
                            progress = (downloaded / total_size) * 100
                            try:
                                await status.edit_text(
                                    f"📁 **{filename}**\n"
                                    f"⬇️ **Downloading:** {progress:.1f}%"
                                )
                            except:
                                pass
        
        # Upload to Telegram
        await status.edit_text(f"📤 **Uploading to Telegram...**")
        
        try:
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
            
            await status.delete()
            
        except Exception as upload_error:
            await status.edit_text(f"❌ **Upload failed:** {str(upload_error)}")
        
        # Cleanup
        try:
            file_path.unlink(missing_ok=True)
        except:
            pass
            
    except Exception as e:
        LOGGER.error(f"Process error: {e}")
        await status.edit_text(f"❌ **Error:** {str(e)}")

def format_size(bytes_size):
    """Format file size"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.1f} TB"

async def main():
    """Main function - WITH HEALTH CHECK"""
    try:
        # Start health check server first
        await start_health_server()
        
        # Start bot
        await app.start()
        me = await app.get_me()
        LOGGER.info(f"✅ Bot @{me.username} started successfully!")
        print(f"🚀 Bot @{me.username} is running!")
        print(f"🌐 Health check server running on port 8000")
        
        await idle()
    except Exception as e:
        LOGGER.error(f"❌ Bot startup error: {e}")
    finally:
        try:
            if app.is_connected:
                await app.stop()
        except:
            pass

if __name__ == "__main__":
    asyncio.run(main())
        
