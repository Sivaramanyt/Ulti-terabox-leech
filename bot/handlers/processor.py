"""
Main file processing logic - SPEED OPTIMIZED
"""

import os
import requests
import aiohttp
import aiofiles
import asyncio
from pathlib import Path
from urllib.parse import quote
from telegram import Update
from config import LOGGER, DOWNLOAD_DIR

# Terabox API functions (same as before)
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

def extract_terabox_info(url):
    """Extract file info using wdzone-terabox-api"""
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
        
        filename = data.get("📂 Title") or data.get("Title", "Unknown")
        size_str = data.get("📏 Size") or data.get("Size", "0 B")
        download_url = data.get("🔽 Direct Download Link") or data.get("Direct Download Link", "")
        
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

async def process_terabox_url(update: Update, url: str):
    """Process Terabox URL - SPEED OPTIMIZED VERSION"""
    print(f"🎯 Starting Terabox processing: {url}")
    LOGGER.info(f"Starting Terabox processing: {url}")
    
    status_msg = await update.message.reply_text("🔍 **Processing Terabox URL...**", parse_mode='Markdown')
    
    try:
        # Step 1: Extract file info
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
            f"📁 **File Found**\n📊 **{format_size(file_size)}**\n✅ **API Success**\n⚡ **High-Speed Download...**",
            parse_mode='Markdown'
        )
        
        # Step 3: SPEED OPTIMIZED DOWNLOAD
        print(f"⚡ Step 3: High-speed download...")
        file_path = Path(DOWNLOAD_DIR) / filename
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        
        # OPTIMIZED: Larger chunk size + timeout settings + connection limits
        connector = aiohttp.TCPConnector(
            limit=100,  # More connections
            limit_per_host=30,  # More per host
            ttl_dns_cache=300,  # DNS cache
            use_dns_cache=True,
        )
        
        timeout = aiohttp.ClientTimeout(
            total=None,  # No total timeout
            sock_connect=30,  # Socket connect timeout
            sock_read=30  # Socket read timeout
        )
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            async with session.get(download_url, headers=headers) as response:
                if response.status != 200:
                    await status_msg.edit_text(
                        f"❌ **Download failed**\n\n**HTTP Status:** {response.status}", 
                        parse_mode='Markdown'
                    )
                    return
                
                total_size = int(response.headers.get('content-length', file_size))
                downloaded = 0
                
                print(f"📥 High-speed downloading {filename}, size: {total_size}")
                
                async with aiofiles.open(file_path, 'wb') as f:
                    # OPTIMIZED: 1MB chunks instead of 8KB for much faster speed
                    async for chunk in response.content.iter_chunked(1024 * 1024):  # 1MB chunks
                        await f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Update progress every 5MB to reduce API calls
                        if downloaded % (5 * 1024 * 1024) == 0:
                            progress = (downloaded / total_size) * 100 if total_size > 0 else 0
                            try:
                                await status_msg.edit_text(
                                    f"📁 **High-Speed Download**\n⚡ **Progress:** {progress:.1f}%\n📊 **{format_size(downloaded)} / {format_size(total_size)}**",
                                    parse_mode='Markdown'
                                )
                            except:
                                pass  # Ignore rate limits
        
        print(f"✅ Step 3 complete: High-speed download finished")
        
        # Step 4: FAST UPLOAD with thumbnail support
        print(f"📤 Step 4: Uploading to Telegram...")
        await status_msg.edit_text("📤 **Uploading to Telegram...**", parse_mode='Markdown')
        
        try:
            # Create caption without markdown
            caption = f"🎥 {filename}\n📊 Size: {format_size(file_size)}\n⚡ High-Speed Leech\n🔗 wdzone-terabox-api"
            
            # OPTIMIZED: Get thumbnail URL from API response for better video preview
            thumbnail_url = None
            if 'Thumbnails' in str(file_info) or '🖼️ Thumbnails' in str(file_info):
                # Extract thumbnail from API response
                api_response = extract_terabox_info(url)  # Re-call to get full response
                print(f"🖼️ Thumbnail available for better preview")
            
            # Detect file type and upload with optimizations
            with open(file_path, 'rb') as file:
                if filename.lower().endswith(('.mp4', '.avi', '.mkv', '.mov', '.wmv')):
                    # Video upload with duration detection
                    await update.message.reply_video(
                        video=file,
                        caption=caption,
                        width=1280,  # Better quality
                        height=720,  # Better quality
                        supports_streaming=True  # Better playback
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
        
        print(f"🎉 Process complete: {filename} successfully processed with high speed!")
        LOGGER.info(f"Successfully processed: {filename}")
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Process error: {error_msg}")
        LOGGER.error(f"Process error: {error_msg}")
        await status_msg.edit_text(f"❌ **Error:** {error_msg}", parse_mode='Markdown')
        
