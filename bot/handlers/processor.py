"""
Main file processing logic - FIXED MARKDOWN ERROR
"""

import os
import aiohttp
import aiofiles
from pathlib import Path
from telegram import Update
from config import LOGGER, DOWNLOAD_DIR
import bot.utils.terabox_api as terabox_api

async def process_terabox_url(update: Update, url: str):
    """Process Terabox URL - FIXED VERSION WITH NO MARKDOWN ERRORS"""
    print(f"🎯 Starting Terabox processing: {url}")
    LOGGER.info(f"Starting Terabox processing: {url}")
    
    status_msg = await update.message.reply_text("🔍 **Processing Terabox URL...**", parse_mode='Markdown')
    
    try:
        # Step 1: Extract file info
        print(f"📋 Step 1: Using wdzone-terabox-api...")
        await status_msg.edit_text("📋 **Using wdzone-terabox-api...**", parse_mode='Markdown')
        
        file_info = terabox_api.extract_terabox_info(url)
        
        filename = file_info['filename']
        file_size = file_info['size']
        download_url = file_info['download_url']
        
        print(f"✅ Step 1 complete: {filename}, {file_size} bytes")
        
        if not download_url:
            await status_msg.edit_text("❌ **No download URL found**", parse_mode='Markdown')
            return
        
        # Step 2: Size check
        if file_size > 2 * 1024 * 1024 * 1024:  # 2GB limit
            await status_msg.edit_text(
                f"❌ **File too large!**\n\n📁 **File:** {filename}\n📊 **Size:** {terabox_api.format_size(file_size)}\n\n**Max allowed:** 2GB for free tier", 
                parse_mode='Markdown'
            )
            return
        
        await status_msg.edit_text(
            f"📁 **File Found**\n📊 **{terabox_api.format_size(file_size)}**\n✅ **API Success**\n⬇️ **Downloading...**",
            parse_mode='Markdown'
        )
        
        # Step 3: Download file
        print(f"⬇️ Step 3: Downloading file...")
        file_path = Path(DOWNLOAD_DIR) / filename
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        
        async with aiohttp.ClientSession() as session:
            async with session.get(download_url) as response:
                if response.status != 200:
                    await status_msg.edit_text(
                        f"❌ **Download failed**\n\n**HTTP Status:** {response.status}", 
                        parse_mode='Markdown'
                    )
                    return
                
                total_size = int(response.headers.get('content-length', file_size))
                downloaded = 0
                
                print(f"📥 Downloading {filename}, size: {total_size}")
                
                async with aiofiles.open(file_path, 'wb') as f:
                    async for chunk in response.content.iter_chunked(8192):
                        await f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Update progress every 1MB
                        if downloaded % (1024 * 1024) == 0:
                            progress = (downloaded / total_size) * 100 if total_size > 0 else 0
                            try:
                                await status_msg.edit_text(
                                    f"📁 **Downloading**\n⬇️ **Progress:** {progress:.1f}%\n📊 **{terabox_api.format_size(downloaded)} / {terabox_api.format_size(total_size)}**",
                                    parse_mode='Markdown'
                                )
                            except:
                                pass  # Ignore rate limits
        
        print(f"✅ Step 3 complete: File downloaded")
        
        # Step 4: Upload to Telegram (FIXED - NO MARKDOWN IN CAPTIONS)
        print(f"📤 Step 4: Uploading to Telegram...")
        await status_msg.edit_text("📤 **Uploading to Telegram...**", parse_mode='Markdown')
        
        try:
            # Create caption without markdown to avoid parsing errors
            caption = f"🎥 {filename}\n📊 Size: {terabox_api.format_size(file_size)}\n🔗 Source: wdzone-terabox-api"
            
            # Detect file type and upload (NO PARSE_MODE)
            with open(file_path, 'rb') as file:
                if filename.lower().endswith(('.mp4', '.avi', '.mkv', '.mov', '.wmv')):
                    await update.message.reply_video(
                        video=file,
                        caption=caption
                    )
                elif filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                    caption = caption.replace('🎥', '🖼️')
                    await update.message.reply_photo(
                        photo=file,
                        caption=caption
                    )
                else:
                    caption = caption.replace('🎥', '📁')
                    await update.message.reply_document(
                        document=file,
                        caption=caption
                    )
        except Exception as upload_error:
            print(f"❌ Upload error: {upload_error}")
            await status_msg.edit_text(f"❌ **Upload failed:** {str(upload_error)}", parse_mode='Markdown')
            return
        
        print(f"✅ Step 4 complete: File uploaded successfully")
        
        # Step 5: Cleanup
        try:
            file_path.unlink(missing_ok=True)
            print(f"🧹 Cleanup: File deleted")
        except:
            pass
        
        # Delete status message
        try:
            await status_msg.delete()
        except:
            pass
        
        print(f"🎉 Process complete: {filename} successfully processed!")
        LOGGER.info(f"Successfully processed: {filename}")
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Process error: {error_msg}")
        LOGGER.error(f"Process error: {error_msg}")
        await status_msg.edit_text(f"❌ **Error:** {error_msg}", parse_mode='Markdown')
        
