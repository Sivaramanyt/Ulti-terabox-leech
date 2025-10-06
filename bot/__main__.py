"""
Ultra Simple Terabox Leech Bot - DEBUG VERSION
Added debugging to see why commands aren't working
"""

from pyrogram import Client, idle, filters
from pyrogram.types import Message
from config import BOT_TOKEN, TELEGRAM_API, TELEGRAM_HASH, LOGGER, DOWNLOAD_DIR, OWNER_ID
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

# Health check server
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

# DEBUG: Log all messages
@app.on_message()
async def debug_all_messages(client, message: Message):
    """Debug: Log all incoming messages"""
    LOGGER.info(f"📨 Received message from {message.from_user.id}: {message.text}")
    print(f"📨 DEBUG: User {message.from_user.id} sent: {message.text}")
    print(f"📨 DEBUG: OWNER_ID is: {OWNER_ID}")
    print(f"📨 DEBUG: User ID matches owner: {message.from_user.id == OWNER_ID}")

# Start command handler
@app.on_message(filters.command("start"))
async def start_handler(client, message: Message):
    """Start command - UNRESTRICTED"""
    print(f"🚀 DEBUG: Start command received from {message.from_user.id}")
    LOGGER.info(f"Start command from user {message.from_user.id}")
    
    try:
        await message.reply_text("""
🚀 **Ultra Simple Terabox Leech Bot**

**Usage:**
• `/leech <terabox_url>`
• Just send Terabox URL directly

**Features:**
• ⚡ Lightning fast
• 🎯 Terabox only  
• 💾 Memory optimized
• 🆓 Free tier friendly

**Debug Info:**
• Your ID: `{}`
• Owner ID: `{}`
• Bot Status: ✅ WORKING

Send me a Terabox link to get started! 📂
        """.format(message.from_user.id, OWNER_ID))
        
        print(f"✅ DEBUG: Start reply sent successfully")
        
    except Exception as e:
        print(f"❌ DEBUG: Start reply failed: {e}")
        LOGGER.error(f"Start reply error: {e}")

# Test command
@app.on_message(filters.command("test"))
async def test_handler(client, message: Message):
    """Test command"""
    await message.reply_text("🧪 **Test successful!** Bot is responding to commands.")

# Echo command for debugging
@app.on_message(filters.text & ~filters.command(["start", "test", "leech"]))
async def echo_handler(client, message: Message):
    """Echo messages for debugging"""
    await message.reply_text(f"📢 **Echo:** {message.text}\n\n🆔 **Your ID:** `{message.from_user.id}`\n🤖 **I'm working!**")

# Simple Terabox function (simplified for debugging)
def extract_terabox_info(url):
    """Extract file info from Terabox URL"""
    import requests
    
    try:
        if 'surl=' in url:
            surl = url.split('surl=')[-1].split('&')[0]
        elif '/s/' in url:
            surl = url.split('/s/')[-1].split('?')[0]
        else:
            raise Exception("Invalid Terabox URL")
        
        api_url = "https://www.terabox.com/api/shorturlinfo"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
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

@app.on_message(filters.command("leech"))
async def leech_command(client, message: Message):
    """Leech command handler"""
    print(f"📥 DEBUG: Leech command from {message.from_user.id}")
    
    if len(message.command) < 2:
        await message.reply_text("❌ **Usage:** `/leech https://terabox.com/s/xxxxx`")
        return
    
    await message.reply_text("🔍 **Processing Terabox URL...**\n\n⚠️ **Note:** This is a debug version. Full download functionality will be restored once commands are working.")

@app.on_message(filters.regex(r"terabox\.com") & filters.text & ~filters.command(["start", "leech", "test"]))
async def auto_leech(client, message: Message):
    """Auto-detect Terabox URLs"""
    await message.reply_text("🔗 **Terabox URL detected!**\n\n⚠️ **Note:** This is a debug version. Use `/leech <url>` command instead.")

def format_size(bytes_size):
    """Format file size"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.1f} TB"

async def main():
    """Main function - DEBUG VERSION"""
    try:
        await start_health_server()
        await app.start()
        
        me = await app.get_me()
        LOGGER.info(f"✅ Bot @{me.username} started successfully!")
        print(f"🚀 Bot @{me.username} is running!")
        print(f"🌐 Health check server running on port 8000")
        print(f"🔍 DEBUG MODE: All messages will be logged")
        print(f"🆔 OWNER_ID: {OWNER_ID}")
        print(f"🤖 Bot ID: {me.id}")
        
        await idle()
    except Exception as e:
        LOGGER.error(f"❌ Bot startup error: {e}")
        print(f"❌ ERROR: {e}")
    finally:
        try:
            if app.is_connected:
                await app.stop()
        except:
            pass

if __name__ == "__main__":
    asyncio.run(main())
    
