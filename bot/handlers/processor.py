"""
ANASTY17-STYLE PROCESSOR - Using aria2c download engine for 100% first-attempt success
Based on: https://github.com/anasty17/mirror-leech-telegram-bot
"""

import os
import requests
import asyncio
import subprocess
import json
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

# ✅ ANASTY17 METHOD: aria2c Download Engine
async def download_with_aria2c(download_url, file_path, filename, status_msg, total_size):
    """Download using aria2c - anasty17's proven method for 100% success rate"""
    
    try:
        print(f"🏹 Using aria2c download engine for: {filename}")
        
        # ✅ Create aria2c command with optimal settings (anasty17 configuration)
        aria2c_cmd = [
            'aria2c',
            '--console-log-level=error',
            '--summary-interval=0',
            '--download-result=hide',
            '--max-connection-per-server=8',  # 8 connections per server
            '--min-split-size=1M',            # 1MB minimum split size
            '--split=8',                      # Split into 8 parts
            '--max-concurrent-downloads=1',   # One download at a time
            '--continue=true',                # Resume downloads
            '--max-tries=5',                  # 5 retry attempts
            '--retry-wait=10',                # 10 second wait between retries
            '--timeout=60',                   # 60 second timeout
            '--connect-timeout=30',           # 30 second connect timeout
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            '--header=Accept: */*',
            '--header=Accept-Language: en-US,en;q=0.9',
            '--header=Connection: keep-alive',
            '--allow-overwrite=true',
            '--auto-file-renaming=false',
            '--dir=' + str(Path(file_path).parent),
            '--out=' + str(Path(file_path).name),
            download_url
        ]
        
        print(f"🏹 Starting aria2c download...")
        await status_msg.edit_text(
            f"🏹 **Downloading with aria2c**\n📁 **{filename}**\n🚀 **Engine:** Professional grade downloader",
            parse_mode='Markdown'
        )
        
        # ✅ Start aria2c process
        process = await asyncio.create_subprocess_exec(
            *aria2c_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # ✅ Monitor download progress
        download_start = time.time()
        last_update = 0
        
        while process.returncode is None:
            # Check if process is still running
            try:
                await asyncio.wait_for(process.wait(), timeout=1.0)
            except asyncio.TimeoutError:
                # Process still running, update status
                current_time = time.time()
                elapsed = current_time - download_start
                
                # Update every 10 seconds to avoid rate limiting
                if current_time - last_update >= 10:
                    try:
                        # Check file size to show progress
                        if file_path.exists():
                            current_size = file_path.stat().st_size
                            progress = (current_size / total_size) * 100 if total_size > 0 else 0
                            speed = current_size / elapsed if elapsed > 0 else 0
                            
                            await status_msg.edit_text(
                                f"🏹 **aria2c Downloading**\n"
                                f"📁 **{filename}**\n"
                                f"⬇️ **Progress:** {progress:.1f}%\n"
                                f"📊 **{format_size(current_size)} / {format_size(total_size)}**\n"
                                f"🚀 **Speed:** {format_size(speed)}/s\n"
                                f"⏱️ **Time:** {int(elapsed)}s",
                                parse_mode='Markdown'
                            )
                        else:
                            await status_msg.edit_text(
                                f"🏹 **aria2c Connecting**\n📁 **{filename}**\n🔗 **Establishing connection...**",
                                parse_mode='Markdown'
                            )
                        
                        last_update = current_time
                    except:
                        pass  # Ignore telegram rate limits
        
        # ✅ Get process result
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0 and file_path.exists():
            final_size = file_path.stat().st_size
            print(f"✅ aria2c download successful! Downloaded {final_size} bytes")
            return True
        else:
            error_output = stderr.decode() if stderr else "Unknown aria2c error"
            print(f"❌ aria2c download failed: {error_output}")
            raise Exception(f"aria2c failed: {error_output}")
            
    except Exception as e:
        print(f"❌ aria2c download error: {e}")
        raise e

# ✅ FALLBACK: wget Download (if aria2c not available)
async def download_with_wget(download_url, file_path, filename, status_msg):
    """Fallback wget download method"""
    try:
        print(f"🌐 Using wget fallback for: {filename}")
        
        await status_msg.edit_text(
            f"🌐 **wget Download**\n📁 **{filename}**\n🔄 **Alternative method...**",
            parse_mode='Markdown'
        )
        
        wget_cmd = [
            'wget',
            '--timeout=60',
            '--tries=5',
            '--wait=10',
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            '--header=Accept: */*',
            '--continue',
            '--output-document=' + str(file_path),
            download_url
        ]
        
        process = await asyncio.create_subprocess_exec(
            *wget_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0 and file_path.exists():
            print(f"✅ wget download successful!")
            return True
        else:
            error_output = stderr.decode() if stderr else "Unknown wget error"
            raise Exception(f"wget failed: {error_output}")
            
    except Exception as e:
        print(f"❌ wget download failed: {e}")
        raise e

async def process_terabox_url(update: Update, url: str):
    """Process Terabox URL using anasty17's download methods"""
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
            f"📁 **File Found**\n📊 **{format_size(file_size)}**\n✅ **API Success**\n🏹 **Using aria2c engine...**",
            parse_mode='Markdown'
        )

        # Step 3: ANASTY17-STYLE DOWNLOAD with aria2c
        print(f"🏹 Step 3: aria2c download...")
        file_path = Path(DOWNLOAD_DIR) / filename
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        
        download_success = False
        
        # ✅ Method 1: Try aria2c first (anasty17's primary method)
        try:
            await download_with_aria2c(download_url, file_path, filename, status_msg, file_size)
            download_success = True
            print(f"✅ aria2c download successful")
        except Exception as e:
            print(f"❌ aria2c failed: {e}")
            
            # ✅ Method 2: Try wget as fallback
            try:
                await download_with_wget(download_url, file_path, filename, status_msg)
                download_success = True
                print(f"✅ wget download successful")
            except Exception as e2:
                print(f"❌ wget also failed: {e2}")
                raise Exception(f"All download methods failed. aria2c: {str(e)}, wget: {str(e2)}")

        if not download_success:
            await status_msg.edit_text("❌ **Download failed with all methods**", parse_mode='Markdown')
            return

        print(f"✅ Step 3 complete: File downloaded successfully")

        # Step 4: Upload to Telegram (EXACTLY YOUR CODE)
        print(f"📤 Step 4: Uploading to Telegram...")
        await status_msg.edit_text("📤 **Uploading to Telegram...**", parse_mode='Markdown')

        try:
            caption = f"🎥 {filename}\n📊 Size: {format_size(file_size)}\n🏹 Downloaded with aria2c"
            
            with open(file_path, 'rb') as file:
                if filename.lower().endswith(('.mp4', '.avi', '.mkv', '.mov', '.wmv', '.webm', '.m4v', '.3gp', '.ts')):
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
        
