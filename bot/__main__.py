"""
Ultra Simple Terabox Leech Bot - TELEGRAM-BOT VERSION
Replaced Pyrogram with python-telegram-bot for better reliability
"""

import asyncio
import logging
import os
from pathlib import Path
import aiohttp
import aiofiles
import requests
from aiohttp import web

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN, TELEGRAM_API, TELEGRAM_HASH, LOGGER, DOWNLOAD_DIR, OWNER_ID

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
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

# Terabox function
def extract_terabox_info(url):
    """Extract file info from Terabox URL"""
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

# Bot handlers
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

**Features:**
• ⚡ Lightning fast
• 🎯 Terabox only  
• 💾 Memory optimized
• 🆓 Free tier friendly

**Debug Info:**
• Your ID: `{user_id}`
• Owner ID: `{OWNER_ID}`
• Bot Status: ✅ WORKING

Send me a Terabox link to get started! 📂
    """
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def test_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Test command"""
    await update.message.reply_text("🧪 **Test successful!** Bot is responding to commands!", parse_mode='Markdown')

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo messages for debugging"""
    user_id = update.effective_user.id
    message_text = update.message.text
    
    LOGGER.info(f"Message from {user_id}: {message_text}")
    print(f"📨 DEBUG: User {user_id} sent: {message_text}")
    
    # Check if it's a Terabox URL
    if 'terabox.com' in message_text.lower():
        await process_terabox_url(update, message_text)
    else:
        await update.message.reply_text(
            f"📢 **Echo:** {message_text}\n\n🆔 **Your ID:** `{user_id}`\n🤖 **I'm working!**",
            parse_mode='Markdown'
        )

async def leech_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Leech command handler"""
    user_id = update.effective_user.id
    LOGGER.info(f"Leech command from user {user_id}")
    print(f"📥 DEBUG: Leech command from {user_id}")
    
    if not context.args:
        await update.message.reply_text("❌ **Usage:** `/leech https://terabox.com/s/xxxxx`", parse_mode='Markdown')
        return
    
    url = context.args[0]
    await process_terabox_url(update, url)

async def process_terabox_url(update: Update, url: str):
    """Process Terabox URL"""
    status_msg = await update.message.reply_text("🔍 **Processing Terabox URL...**", parse_mode='Markdown')
    
    try:
        # Get file info
        await status_msg.edit_text("📋 **Extracting file info...**", parse_mode='Markdown')
        file_info = extract_terabox_info(url)
        
        filename = file_info['filename']
        file_size = file_info['size']
        download_url = file_info['download_url']
        
        if not download_url:
            await status_msg.edit_text("❌ **No download URL found**", parse_mode='Markdown')
            return
        
        # Size check
        if file_size > 2 * 1024 * 1024 * 1024:
            await status_msg.edit_text("❌ **File too large!** Max: 2GB for free tier", parse_mode='Markdown')
            return
        
        await status_msg.edit_text(
            f"📁 **{filename}**\n📊 **{format_size(file_size)}**\n⬇️ **Downloading...**",
            parse_mode='Markdown'
        )
        
        # Download file
        file_path = Path(DOWNLOAD_DIR) / filename
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        
        async with aiohttp.ClientSession() as session:
            async with session.get(download_url) as response:
                if response.status != 200:
                    await status_msg.edit_text(f"❌ **Download failed: HTTP {response.status}**", parse_mode='Markdown')
                    return
                
                async with aiofiles.open(file_path, 'wb') as f:
                    async for chunk in response.content.iter_chunked(8192):
                        await f.write(chunk)
        
        # Upload to Telegram
        await status_msg.edit_text("📤 **Uploading to Telegram...**", parse_mode='Markdown')
        
        # Detect file type and upload
        if filename.lower().endswith(('.mp4', '.avi', '.mkv', '.mov', '.wmv')):
            await update.message.reply_video(
                video=open(file_path, 'rb'),
                caption=f"🎥 **{filename}**",
                parse_mode='Markdown'
            )
        elif filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
            await update.message.reply_photo(
                photo=open(file_path, 'rb'),
                caption=f"🖼️ **{filename}**",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_document(
                document=open(file_path, 'rb'),
                caption=f"📁 **{filename}**",
                parse_mode='Markdown'
            )
        
        # Cleanup
        try:
            file_path.unlink(missing_ok=True)
        except:
            pass
        
        await status_msg.delete()
        
    except Exception as e:
        LOGGER.error(f"Process error: {e}")
        await status_msg.edit_text(f"❌ **Error:** {str(e)}", parse_mode='Markdown')

def format_size(bytes_size):
    """Format file size"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.1f} TB"

async def main():
    """Main function"""
    try:
        # Start health check server
        await start_health_server()
        
        # Create application
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("test", test_handler))
        application.add_handler(CommandHandler("leech", leech_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
        
        print(f"🚀 Bot starting with token: {BOT_TOKEN[:20]}...")
        print(f"🌐 Health check server running on port 8000")
        print(f"🔍 DEBUG MODE: All messages will be logged")
        print(f"🆔 OWNER_ID: {OWNER_ID}")
        
        # Start the bot
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        
        LOGGER.info("✅ Bot started successfully with python-telegram-bot!")
        print("✅ Bot is now running and listening for messages!")
        
        # Keep running
        while True:
            await asyncio.sleep(1)
            
    except Exception as e:
        LOGGER.error(f"❌ Bot startup error: {e}")
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(main())
        
