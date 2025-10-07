"""
ULTIMATE WORKING PROCESSOR - Uses requests instead of aiohttp for downloads
"""

import os
import requests
import aiohttp
import aiofiles
import asyncio
import time
from pathlib import Path
from urllib.parse import quote
from telegram import Update
from config import LOGGER, DOWNLOAD_DIR

# ✅ ALL YOUR FUNCTIONS - EXACTLY PRESERVED
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

# ✅ NEW: REQUESTS-BASED DOWNLOAD (FIXES PAYLOAD COMPLETION ISSUE)
async def download_with_requests(download_url, file_path, filename, status_msg, total_size, max_retries=3):
    """Download using requests library instead of aiohttp - MUCH MORE RELIABLE"""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive'
    }
    
    for attempt in range(1, max_retries + 1):
        try:
            print(f"🔄 Download attempt {attempt}/{max_retries} for {filename}")
            
            # ✅ Use requests.Session for better connection handling
            session = requests.Session()
            session.headers.update(headers)
            
            # ✅ Make request with streaming enabled
            response = session.get(download_url, stream=True, timeout=30)
            response.raise_for_status()  # Raises exception for bad status codes
            
            downloaded = 0
            start_time = time.time()
            
            print(f"📥 Downloading {filename}, size: {total_size}")
            
            # ✅ Download in chunks and write to file
            with open(file_path, 'wb') as f:
                # Use 8KB chunks as in your original code
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # Filter out keep-alive chunks
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Update progress every 1MB as in your original
                        if downloaded % (1024 * 1024) == 0:
                            elapsed_time = time.time() - start_time
                            speed = downloaded / elapsed_time if elapsed_time > 0 else 0
                            progress = (downloaded / total_size) * 100 if total_size > 0 else 0
                            
                            try:
                                # Run update in executor to avoid blocking
                                await asyncio.create_task(
                                    asyncio.to_thread(
                                        lambda: asyncio.create_task(
                                            status_msg.edit_text(
                                                f"📁 **Downloading**\n"
                                                f"⬇️ **Progress:** {progress:.1f}%\n"
                                                f"📊 **{format_size(downloaded)} / {format_size(total_size)}**\n"
                                                f"🚀 **Speed:** {format_size(speed)}/s\n"
                                                f"🔄 **Attempt:** {attempt}/{max_retries}",
                                                parse_mode='Markdown'
                                            )
                                        )
                                    )
                                )
                            except:
                                pass  # Ignore telegram rate limits
            
            session.close()
            print(f"✅ Download attempt {attempt} successful! Downloaded {downloaded} bytes")
            return True
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Download attempt {attempt} failed: {error_msg}")
            
            # Clean up partial file
            try:
                if file_path.exists():
                    file_path.unlink()
            except:
                pass
            
            if attempt < max_retries:
                wait_time = attempt * 10
                print(f"⏳ Waiting {wait_time}s before retry...")
                
                try:
                    await status_msg.edit_text(
                        f"⚠️ **Download failed (Attempt {attempt})**\n\n"
                        f"**Error:** {error_msg[:100]}...\n"
                        f"🔄 **Retrying in {wait_time}s...**\n"
                        f"📊 **Next attempt:** {attempt + 1}/{max_retries}",
                        parse_mode='Markdown'
                    )
                except:
                    pass
                
                await asyncio.sleep(wait_time)
            else:
                raise Exception(f"Download failed after {max_retries} attempts: {error_msg}")

# ✅ ALTERNATIVE: CURL-BASED DOWNLOAD (ULTIMATE FALLBACK)
async def download_with_curl(download_url, file_path, filename, status_msg):
    """Download using curl as ultimate fallback"""
    try:
        print(f"🔧 Using curl fallback for {filename}")
        
        await status_msg.edit_text(
            f"🔧 **Using advanced download method...**\n📁 **File:** {filename}",
            parse_mode='Markdown'
        )
        
        # Use curl command
        curl_cmd = [
            'curl', '-L', '-o', str(file_path), 
            '-H', 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            '--connect-timeout', '30',
            '--max-time', '1800',  # 30 minutes
            '--retry', '3',
            '--retry-delay', '10',
            download_url
        ]
        
        # Run curl command
        process = await asyncio.create_subprocess_exec(
            *curl_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0 and file_path.exists():
            file_size = file_path.stat().st_size
            print(f"✅ Curl download successful! Downloaded {file_size} bytes")
            return True
        else:
            error_msg = stderr.decode() if stderr else "Unknown curl error"
            raise Exception(f"Curl failed: {error_msg}")
            
    except Exception as e:
        print(f"❌ Curl download failed: {e}")
        raise e

async def process_terabox_url(update: Update, url: str):
    """Process Terabox URL with multiple download methods"""
    print(f"🎯 Starting Terabox processing: {url}")
    LOGGER.info(f"Starting Terabox processing: {url}")
    
    status_msg = await update.message.reply_text("🔍 **Processing Terabox URL...**", parse_mode='Markdown')

    try:
        # Step 1: Extract file info (EXACTLY YOUR CODE)
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
                f"❌ **File too large!**\n\n📊 **Size:** {format_size(file_size)}\n**Max allowed:** 2GB",
                parse_mode='Markdown'
            )
            return

        await status_msg.edit_text(
            f"📁 **File Found**\n📊 **{format_size(file_size)}**\n✅ **API Success**\n⬇️ **Downloading...**",
            parse_mode='Markdown'
        )

        # Step 3: ENHANCED DOWNLOAD with multiple methods
        print(f"⬇️ Step 3: Downloading file...")
        file_path = Path(DOWNLOAD_DIR) / filename
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        
        download_success = False
        
        # ✅ Method 1: Try requests-based download first
        try:
            await download_with_requests(download_url, file_path, filename, status_msg, file_size)
            download_success = True
            print(f"✅ Requests download successful")
        except Exception as e:
            print(f"❌ Requests download failed: {e}")
            
            # ✅ Method 2: Try curl as fallback
            try:
                await download_with_curl(download_url, file_path, filename, status_msg)
                download_success = True
                print(f"✅ Curl download successful")
            except Exception as e2:
                print(f"❌ Curl download also failed: {e2}")
                raise Exception(f"All download methods failed. Last error: {str(e2)}")

        if not download_success:
            await status_msg.edit_text("❌ **Download failed with all methods**", parse_mode='Markdown')
            return

        print(f"✅ Step 3 complete: File downloaded successfully")

        # Step 4: Upload to Telegram (EXACTLY YOUR CODE)
        print(f"📤 Step 4: Uploading to Telegram...")
        await status_msg.edit_text("📤 **Uploading to Telegram...**", parse_mode='Markdown')

        try:
            caption = f"🎥 {filename}\n📊 Size: {format_size(file_size)}\n🔗 Source: wdzone-terabox-api"
            
            with open(file_path, 'rb') as file:
                if filename.lower().endswith(('.mp4', '.avi', '.mkv', '.mov', '.wmv', '.webm', '.m4v', '.3gp')):
                    await update.message.reply_video(
                        video=file,
                        caption=caption,
                        width=640,
                        height=480,
                        duration=0,
                        supports_streaming=True,
                        has_spoiler=False
                    )
                elif filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp')):
                    caption = caption.replace('🎥', '🖼️')
                    await update.message.reply_photo(photo=file, caption=caption, has_spoiler=False)
                else:
                    caption = caption.replace('🎥', '📁')
                    await update.message.reply_document(document=file, caption=caption)

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
        
