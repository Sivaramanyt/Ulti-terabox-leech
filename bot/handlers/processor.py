"""
ENHANCED PROCESSOR.PY - Streaming Download + Enhanced Video Upload
Fixed the IncompleteRead error with better streaming approach
"""

import os
import requests
import asyncio
import time
import subprocess
import json
from pathlib import Path
from urllib.parse import quote
from telegram import Update
from config import LOGGER, DOWNLOAD_DIR

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
    """Extract file info using wdzone-terabox-api - WORKING PERFECTLY"""
    try:
        print(f"🔍 Processing URL: {url}")
        LOGGER.info(f"Processing URL: {url}")
        
        apiurl = f"https://wdzone-terabox-api.vercel.app/api?url={quote(url)}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0'
        }

        response = requests.get(apiurl, headers=headers, timeout=30)
        if response.status_code != 200:
            raise Exception(f"API request failed with status: {response.status_code}")
        
        req = response.json()
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

# ✅ ENHANCED VIDEO PROCESSING FUNCTIONS
def get_video_info(video_path):
    """Get video information using ffprobe (if available) or basic fallback"""
    try:
        # Try ffprobe first (best option)
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', '-show_streams', str(video_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            
            for stream in data.get('streams', []):
                if stream.get('codec_type') == 'video':
                    width = stream.get('width', 1280)
                    height = stream.get('height', 720)
                    duration = float(stream.get('duration', 0))
                    print(f"📐 Video detected: {width}x{height}, duration: {duration}s")
                    return width, height, duration
    except Exception as e:
        print(f"⚠️ ffprobe failed: {e}")
    
    # Fallback to HD default values
    print(f"📐 Using default HD resolution: 1280x720")
    return 1280, 720, 0

def generate_video_thumbnail(video_path):
    """Generate thumbnail from video using ffmpeg (if available)"""
    try:
        thumbnail_path = video_path.with_suffix('.jpg')
        
        # Try ffmpeg thumbnail generation
        cmd = [
            'ffmpeg', '-i', str(video_path), '-ss', '00:00:01',
            '-vframes', '1', '-q:v', '2', str(thumbnail_path), '-y'
        ]
        
        result = subprocess.run(cmd, capture_output=True, timeout=30)
        
        if result.returncode == 0 and thumbnail_path.exists():
            print(f"🖼️ Thumbnail generated: {thumbnail_path}")
            return thumbnail_path
        else:
            print(f"⚠️ ffmpeg thumbnail failed")
    except Exception as e:
        print(f"⚠️ Thumbnail generation error: {e}")
    
    return None

# ✅ NEW STREAMING DOWNLOAD METHOD - FIXED FOR TERABOX
async def download_with_streaming(download_url, file_path, filename, status_msg, total_size, max_retries=3):
    """Enhanced streaming download - FIXES IncompleteRead error"""
    
    for attempt in range(1, max_retries + 1):
        try:
            print(f"🌊 Streaming download attempt {attempt}/{max_retries} for {filename}")
            
            # Enhanced headers to avoid detection
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'identity',  # Avoid compression issues
                'Connection': 'keep-alive',
                'Referer': 'https://www.terabox.com/',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'cross-site'
            }
            
            # Create session with retry strategy
            session = requests.Session()
            session.headers.update(headers)
            
            print(f"🌊 Starting streaming download: {filename}")
            
            # Make request with streaming enabled
            response = session.get(
                download_url,
                stream=True,
                timeout=(15, 120),  # 15s connect, 120s read
                allow_redirects=True
            )
            response.raise_for_status()
            
            downloaded = 0
            start_time = time.time()
            last_update = 0
            
            with open(file_path, 'wb') as f:
                # Use 8KB chunks - optimal for most connections
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # Filter out keep-alive chunks
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Update progress every 500KB to avoid rate limits
                        if downloaded - last_update >= 500 * 1024:
                            elapsed_time = time.time() - start_time
                            speed = downloaded / elapsed_time if elapsed_time > 0 else 0
                            progress = (downloaded / total_size) * 100 if total_size > 0 else 0
                            
                            try:
                                await status_msg.edit_text(
                                    f"🌊 **Streaming Download**\n"
                                    f"📁 **{filename}**\n"
                                    f"⬇️ **Progress:** {progress:.1f}%\n"
                                    f"📊 **{format_size(downloaded)} / {format_size(total_size)}**\n"
                                    f"🚀 **Speed:** {format_size(speed)}/s\n"
                                    f"🔄 **Attempt:** {attempt}/{max_retries}",
                                    parse_mode='Markdown'
                                )
                                last_update = downloaded
                            except:
                                pass
                        
                        # Progress logging
                        if downloaded % (5 * 1024 * 1024) == 0:  # Every 5MB
                            print(f"✅ Downloaded: {format_size(downloaded)}")
            
            session.close()
            print(f"✅ Streaming download attempt {attempt} successful! Downloaded {downloaded} bytes")
            return True
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Streaming download attempt {attempt} failed: {error_msg}")
            
            try:
                session.close()
            except:
                pass
                
            # Clean up partial file
            try:
                if file_path.exists():
                    file_path.unlink()
            except:
                pass
            
            if attempt < max_retries:
                wait_time = attempt * 3  # 3s, 6s, 9s
                print(f"⏳ Waiting {wait_time}s before retry...")
                
                try:
                    await status_msg.edit_text(
                        f"⚠️ **Download failed (Attempt {attempt})**\n\n"
                        f"**Error:** {error_msg[:50]}...\n"
                        f"🔄 **Retrying in {wait_time}s...**\n"
                        f"📊 **Next attempt:** {attempt + 1}/{max_retries}",
                        parse_mode='Markdown'
                    )
                except:
                    pass
                
                await asyncio.sleep(wait_time)
            else:
                raise Exception(f"All download attempts failed after {max_retries} tries: {error_msg}")

async def process_terabox_url(update: Update, url: str):
    """Process Terabox URL with enhanced streaming download + video upload"""
    print(f"🎯 Starting enhanced Terabox processing: {url}")
    LOGGER.info(f"Starting enhanced Terabox processing: {url}")
    
    status_msg = await update.message.reply_text("🔍 **Processing Terabox URL...**", parse_mode='Markdown')

    try:
        # Step 1: Extract file info (WORKING PERFECTLY - NO CHANGES)
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
            f"📁 **File Found**\n📊 **{format_size(file_size)}**\n✅ **API Success**\n🌊 **Streaming download...**",
            parse_mode='Markdown'
        )

        # Step 3: ENHANCED STREAMING DOWNLOAD
        print(f"🌊 Step 3: Enhanced streaming download...")
        file_path = Path(DOWNLOAD_DIR) / filename
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        
        await download_with_streaming(download_url, file_path, filename, status_msg, file_size)
        print(f"✅ Step 3 complete: File downloaded successfully")

        # Step 4: ENHANCED UPLOAD TO TELEGRAM
        print(f"📤 Step 4: Enhanced uploading to Telegram...")
        await status_msg.edit_text("📤 **Enhanced uploading to Telegram...**", parse_mode='Markdown')

        try:
            caption = f"🎥 {filename}\n📊 Size: {format_size(file_size)}\n🌊 Streaming download success"
            
            with open(file_path, 'rb') as file:
                if filename.lower().endswith(('.mp4', '.avi', '.mkv', '.mov', '.wmv', '.webm', '.m4v', '.3gp', '.ts')):
                    # ✅ ENHANCED VIDEO UPLOAD
                    print(f"🎬 Uploading as enhanced video...")
                    
                    # Get actual video dimensions and duration
                    width, height, duration = get_video_info(file_path)
                    
                    # Generate thumbnail
                    thumbnail_path = generate_video_thumbnail(file_path)
                    thumbnail_data = None
                    
                    if thumbnail_path and thumbnail_path.exists():
                        try:
                            with open(thumbnail_path, 'rb') as thumb_file:
                                thumbnail_data = thumb_file.read()
                            print(f"🖼️ Thumbnail loaded: {len(thumbnail_data)} bytes")
                            # Clean up thumbnail file
                            thumbnail_path.unlink(missing_ok=True)
                        except Exception as thumb_error:
                            print(f"⚠️ Thumbnail load failed: {thumb_error}")
                            thumbnail_data = None
                    
                    # Upload with enhanced parameters
                    await update.message.reply_video(
                        video=file,
                        caption=caption,
                        width=width,           # ✅ Actual video width
                        height=height,         # ✅ Actual video height  
                        duration=int(duration) if duration > 0 else None,  # ✅ Actual duration
                        thumbnail=thumbnail_data,  # ✅ Generated thumbnail
                        supports_streaming=True,
                        has_spoiler=False,
                        parse_mode='Markdown'
                    )
                    print(f"🎬 Enhanced video upload complete: {width}x{height}")
                    
                elif filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp')):
                    # ✅ ENHANCED IMAGE UPLOAD
                    caption = caption.replace('🎥', '🖼️')
                    await update.message.reply_photo(
                        photo=file, 
                        caption=caption, 
                        has_spoiler=False,
                        parse_mode='Markdown'
                    )
                    print(f"🖼️ Enhanced image upload complete")
                else:
                    # ✅ ENHANCED DOCUMENT UPLOAD  
                    caption = caption.replace('🎥', '📁')
                    await update.message.reply_document(
                        document=file, 
                        caption=caption,
                        parse_mode='Markdown'
                    )
                    print(f"📁 Enhanced document upload complete")

        except Exception as upload_error:
            print(f"❌ Upload error: {upload_error}")
            await status_msg.edit_text(f"❌ **Upload failed:** {str(upload_error)}", parse_mode='Markdown')
            return

        print(f"✅ Step 4 complete: Enhanced upload successful")

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

        print(f"🎉 Process complete: {filename} successfully processed with enhancements!")
        LOGGER.info(f"Successfully processed: {filename} with enhanced streaming download")

    except Exception as e:
        error_msg = str(e)
        print(f"❌ Process error: {error_msg}")
        LOGGER.error(f"Process error: {error_msg}")
        await status_msg.edit_text(f"❌ **Error:** {error_msg}", parse_mode='Markdown')
        
