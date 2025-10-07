"""
Ultra Terabox Processor - Based on WORKING wdzone-terabox-api
Enhanced with filename cleaning + better error handling
"""

import os
import requests
import aiohttp
import aiofiles
from pathlib import Path
from urllib.parse import quote
from telegram import Update
from telegram.ext import ContextTypes
from config import LOGGER, DOWNLOAD_DIR, FREE_DOWNLOAD_LIMIT
import re

def speed_string_to_bytes(size_str):
    """Convert size string to bytes"""
    size_str = size_str.replace(" ", "").upper()
    if "KB" in size_str:
        return float(size_str.replace("KB", "")) * 1024
    elif "MB" in size_str:
        return float(size_str.replace("MB", "")) * 1024 * 1024
    elif "GB" in size_str:
        return float(size_str.replace("GB", "")) * 1024 * 1024 * 1024
    elif "TB" in size_str:
        return float(size_str.replace("TB", "")) * 1024 * 1024 * 1024 * 1024
    else:
        try:
            return float(size_str.replace("B", ""))
        except:
            return 0

def clean_filename(filename):
    """Clean filename from Terabox titles and invalid characters"""
    try:
        # Remove common Terabox page suffixes
        patterns = [
            r'\s*-\s*Share Files Online.*',
            r'\s*-\s*TeraBox.*',
            r'\s*&amp;.*',
            r'\s*\|\s*TeraBox.*'
        ]
        
        cleaned = filename
        for pattern in patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Remove HTML entities
        cleaned = cleaned.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        
        # Remove invalid filename characters
        cleaned = re.sub(r'[<>:"/\\|?*]', '', cleaned).strip()
        
        # Ensure reasonable length
        if len(cleaned) > 100:
            parts = cleaned.rsplit('.', 1)
            if len(parts) == 2:
                cleaned = parts[0][:90] + '.' + parts[1]
            else:
                cleaned = cleaned[:100]
        
        # Add extension if missing
        extensions = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.jpg', '.png', '.pdf', '.zip']
        if not any(cleaned.lower().endswith(ext) for ext in extensions):
            if any(word in cleaned.lower() for word in ['video', 'movie', 'mp4', 'vid']):
                cleaned += '.mp4'
            else:
                cleaned += '.mp4'  # Default
        
        return cleaned if cleaned else 'terabox_file.mp4'
    except:
        return 'terabox_file.mp4'

def extract_terabox_info(url):
    """Extract file info using wdzone-terabox-api - PROVEN WORKING"""
    try:
        print(f"🔍 Processing URL: {url}")
        LOGGER.info(f"Processing URL: {url}")
        
        apiurl = f"https://wdzone-terabox-api.vercel.app/api?url={quote(url)}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0'
        }
        
        print(f"🌐 API URL: {apiurl}")
        LOGGER.info(f"Making API request to: {apiurl}")
        
        response = requests.get(apiurl, headers=headers, timeout=30)
        if response.status_code != 200:
            raise Exception(f"API request failed with status: {response.status_code}")
        
        req = response.json()
        print(f"📄 API Response: {req}")
        LOGGER.info(f"API response: {req}")
        
        extracted_info = None
        if "✅ Status" in req and req["✅ Status"] == "Success":
            extracted_info = req.get("📜 Extracted Info", [])
        elif "Status" in req and req["Status"] == "Success":
            extracted_info = req.get("Extracted Info", [])
        else:
            if "❌ Status" in req:
                error_msg = req.get("📜 Message", "Unknown error")
                raise Exception(f"API Error: {error_msg}")
            else:
                raise Exception("Invalid API response format")
        
        if not extracted_info:
            raise Exception("No files found")
        
        data = extracted_info[0]
        raw_filename = data.get("📂 Title") or data.get("Title", "Unknown")
        size_str = data.get("📏 Size") or data.get("Size", "0 B")
        download_url = data.get("🔽 Direct Download Link") or data.get("Direct Download Link", "")
        
        # ENHANCED: Clean the filename
        filename = clean_filename(raw_filename)
        
        result = {
            'filename': filename,
            'size': speed_string_to_bytes(size_str.replace(" ", "")),
            'download_url': download_url,
            'type': 'file'
        }
        
        print(f"✅ File info extracted: {result}")
        LOGGER.info(f"File extracted: {result}")
        return result
        
    except Exception as e:
        print(f"❌ Terabox extraction error: {e}")
        LOGGER.error(f"Terabox extraction error: {e}")
        raise Exception(f"Failed to process Terabox link: {str(e)}")

def format_size(bytes_size):
    """Format file size"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.1f} TB"

async def process_terabox_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process Terabox URL - ENHANCED WORKING VERSION"""
    message = update.message
    user_id = message.from_user.id
    url = message.text.strip()
    
    print(f"🎯 Starting Terabox processing: {url}")
    LOGGER.info(f"Starting Terabox processing: {url}")
    
    # Check user limits (placeholder - implement as needed)
    user_downloads = get_user_download_count(user_id)
    if user_downloads >= FREE_DOWNLOAD_LIMIT and not is_user_verified(user_id):
        await send_verification_required_message(message, user_id, user_downloads)
        return
    
    status_msg = await message.reply_text("🔍 **Processing Terabox URL...**", parse_mode='Markdown')
    
    try:
        # Step 1: Extract file info using WORKING API
        print(f"📋 Step 1: Using wdzone-terabox-api...")
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
                f"❌ **File too large!**\n\n📊 **Size:** {format_size(file_size)}\n\n**Max allowed:** 2GB for free tier",
                parse_mode='Markdown'
            )
            return
        
        await status_msg.edit_text(
            f"📁 **File Found**\n📊 **{format_size(file_size)}**\n✅ **API Success**\n⬇️ **Downloading...**",
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
                    async for chunk in response.content.iter_chunked(8192):  # 8KB chunks
                        await f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Update progress every 1MB
                        if downloaded % (1024 * 1024) == 0:
                            progress = (downloaded / total_size) * 100 if total_size > 0 else 0
                            try:
                                await status_msg.edit_text(
                                    f"📁 **Downloading**\n⬇️ **Progress:** {progress:.1f}%\n📊 **{format_size(downloaded)} / {format_size(total_size)}**",
                                    parse_mode='Markdown'
                                )
                            except:
                                pass  # Ignore rate limits
        
        print(f"✅ Step 3 complete: File downloaded")
        
        # Step 4: Upload to Telegram - ENHANCED WITH BETTER MEDIA HANDLING
        print(f"📤 Step 4: Uploading to Telegram...")
        await status_msg.edit_text("📤 **Uploading to Telegram...**", parse_mode='Markdown')
        
        try:
            caption = f"📁 **{filename}**\n📊 **Size:** {format_size(file_size)}\n🔗 **Source:** Terabox\n✅ **Enhanced processor with clean filename**"
            
            with open(file_path, 'rb') as file:
                if filename.lower().endswith(('.mp4', '.avi', '.mkv', '.mov', '.wmv', '.webm', '.m4v', '.3gp')):
                    # ENHANCED VIDEO UPLOAD
                    await message.reply_video(
                        video=file,
                        caption=caption,
                        width=640,
                        height=480,
                        duration=0,
                        supports_streaming=True,
                        parse_mode='Markdown'
                    )
                elif filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp')):
                    # ENHANCED IMAGE UPLOAD
                    await message.reply_photo(
                        photo=file,
                        caption=caption,
                        parse_mode='Markdown'
                    )
                else:
                    # ENHANCED DOCUMENT UPLOAD
                    await message.reply_document(
                        document=file,
                        caption=caption,
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
        
        # Update user stats
        increment_user_downloads(user_id)
        
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

# Database helper functions (implement as needed)
def get_user_download_count(user_id):
    return 0

def is_user_verified(user_id):
    return False

def increment_user_downloads(user_id):
    pass

async def send_verification_required_message(message, user_id, download_count):
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    keyboard = [
        [InlineKeyboardButton("🔓 Start Verification", callback_data="start_verification")],
        [InlineKeyboardButton("📊 My Status", callback_data="status")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await message.reply_text(
        f"🔐 **Verification Required**\n\n"
        f"Free downloads used: **{download_count}/{FREE_DOWNLOAD_LIMIT}**\n\n"
        f"Complete verification for unlimited downloads:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
        )
        
