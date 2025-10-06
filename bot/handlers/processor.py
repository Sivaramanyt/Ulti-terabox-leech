"""
Main file processing logic - Using anasty17's API
"""

import os
import aiohttp
import aiofiles
from pathlib import Path
from telegram import Update
from config import LOGGER, DOWNLOAD_DIR
from ..utils.terabox_extractor import extract_terabox_info, format_size

async def process_terabox_url(update: Update, url: str):
    """Process Terabox URL using anasty17's EXACT method"""
    print(f"🎯 Starting Terabox processing: {url}")
    LOGGER.info(f"Starting Terabox processing: {url}")
    
    status_msg = await update.message.reply_text("🔍 **Processing Terabox URL...**", parse_mode='Markdown')
    
    try:
        # Step 1: Extract file info using anasty17's API
        print(f"📋 Step 1: Using anasty17's wdzone-terabox-api...")
        await status_msg.edit_text("📋 **Using wdzone-terabox-api...**", parse_mode='Markdown')
        
        file_info = extract_terabox_info(url)
        
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
                f"❌ **File too large!**\n\n📁 **File:** {filename}\n📊 **Size:** {format_size(file_size)}\n\n**Max allowed:** 2GB for free tier", 
                parse_mode='Markdown'
            )
            return
        
        await status_msg.edit_text(
            f"📁 **{filename}**\n📊 **{format_size(file_size)}**\n✅ **API Success**\n⬇️ **Downloading...**",
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
                        f"❌ **Download failed**\n\n**HTTP Status:** {response.status}\n**File:** {filename}", 
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
                                    f"📁 **{filename}**\n⬇️ **Downloading:** {progress:.1f}%\n📊 **{format_size(downloaded)} / {format_size(total_size)}**",
                                    parse_mode='Markdown'
                                )
                            except:
                                pass  # Ignore rate limits
        
        print(f"✅ Step 3 complete: File downloaded")
        
        # Step 4: Upload to Telegram
        print(f"📤 Step 4: Uploading to Telegram...")
        await status_msg.edit_text(f"📤 **Uploading to Telegram...**\n\n📁 **{filename}**", parse_mode='Markdown')
        
        try:
            # Detect file type and upload
            with open(file_path, 'rb') as file:
                if filename.lower().endswith(('.mp4', '.avi', '.mkv', '.mov', '.wmv')):
                    await update.message.reply_video(
                        video=file,
                        caption=f"🎥 **{filename}**\n📊 **Size:** {format_size(file_size)}\n🔗 **Source:** wdzone-terabox-api",
                        parse_mode='Markdown'
                    )
                elif filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                    await update.message.reply_photo(
                        photo=file,
                        caption=f"🖼️ **{filename}**\n📊 **Size:** {format_size(file_size)}\n🔗 **Source:** wdzone-terabox-api",
                        parse_mode='Markdown'
                    )
                else:
                    await update.message.reply_document(
                        document=file,
                        caption=f"📁 **{filename}**\n📊 **Size:** {format_size(file_size)}\n🔗 **Source:** wdzone-terabox-api",
                        parse_mode='Markdown'
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
