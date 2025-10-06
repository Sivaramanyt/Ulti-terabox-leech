"""
Enhanced processor with anasty17's techniques - OPTIONAL ENHANCED MODE
Falls back to simple version if enhanced fails
"""

import os
import asyncio
import aiohttp
import aiofiles
from pathlib import Path
from urllib.parse import quote
from telegram import Update
from config import LOGGER, DOWNLOAD_DIR
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from concurrent.futures import ThreadPoolExecutor
import time

# Import your working processor as fallback
try:
    from .processor import process_terabox_url as simple_process_terabox_url
    from .processor import extract_terabox_info, format_size
    FALLBACK_AVAILABLE = True
except ImportError:
    FALLBACK_AVAILABLE = False

class EnhancedDownloader:
    """Enhanced downloader using anasty17's techniques"""
    
    def __init__(self):
        self.max_connections = 4  # Multiple connections for speed
        self.chunk_size = 1024 * 1024  # 1MB chunks for speed
        self.max_retries = 3
        self.timeout = aiohttp.ClientTimeout(total=None, sock_read=30)
        
    @retry(
        wait=wait_exponential(multiplier=2, min=4, max=8),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(Exception)
    )
    async def download_with_retry(self, session, url, file_path, progress_callback=None):
        """Download with automatic retry using anasty17's retry logic"""
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"HTTP {response.status}")
                
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                async with aiofiles.open(file_path, 'wb') as f:
                    async for chunk in response.content.iter_chunked(self.chunk_size):
                        await f.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback and downloaded % (2 * 1024 * 1024) == 0:  # Every 2MB
                            await progress_callback(downloaded, total_size)
                
                return downloaded
                
        except Exception as e:
            LOGGER.error(f"Download attempt failed: {e}")
            raise
    
    async def multi_connection_download(self, url, file_path, total_size, progress_callback=None):
        """Multi-connection download like anasty17's aria2c implementation"""
        if total_size < 10 * 1024 * 1024:  # Files < 10MB, use single connection
            return await self.single_connection_download(url, file_path, progress_callback)
        
        # For larger files, use multiple connections
        part_size = total_size // self.max_connections
        tasks = []
        temp_files = []
        
        connector = aiohttp.TCPConnector(
            limit=self.max_connections * 2,
            limit_per_host=self.max_connections,
            ttl_dns_cache=300,
            use_dns_cache=True,
        )
        
        try:
            async with aiohttp.ClientSession(
                connector=connector, 
                timeout=self.timeout
            ) as session:
                
                for i in range(self.max_connections):
                    start = i * part_size
                    end = start + part_size - 1 if i < self.max_connections - 1 else total_size - 1
                    
                    temp_file = f"{file_path}.part_{i}"
                    temp_files.append(temp_file)
                    
                    task = self.download_part(session, url, temp_file, start, end, progress_callback)
                    tasks.append(task)
                
                # Download all parts concurrently
                await asyncio.gather(*tasks)
                
                # Combine parts into final file
                await self.combine_parts(temp_files, file_path)
                
                return total_size
                
        finally:
            # Cleanup temp files
            for temp_file in temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                except:
                    pass
    
    async def download_part(self, session, url, temp_file, start, end, progress_callback):
        """Download a specific part of the file"""
        headers = {'Range': f'bytes={start}-{end}'}
        
        async with session.get(url, headers=headers) as response:
            if response.status not in [200, 206]:
                raise Exception(f"Part download failed: HTTP {response.status}")
            
            async with aiofiles.open(temp_file, 'wb') as f:
                async for chunk in response.content.iter_chunked(self.chunk_size):
                    await f.write(chunk)
    
    async def combine_parts(self, temp_files, final_file):
        """Combine downloaded parts into final file"""
        async with aiofiles.open(final_file, 'wb') as outfile:
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    async with aiofiles.open(temp_file, 'rb') as infile:
                        while True:
                            chunk = await infile.read(self.chunk_size)
                            if not chunk:
                                break
                            await outfile.write(chunk)
    
    async def single_connection_download(self, url, file_path, progress_callback=None):
        """Single connection download with enhanced settings"""
        connector = aiohttp.TCPConnector(
            limit=30,
            ttl_dns_cache=300,
            use_dns_cache=True,
        )
        
        async with aiohttp.ClientSession(
            connector=connector, 
            timeout=self.timeout
        ) as session:
            return await self.download_with_retry(session, url, file_path, progress_callback)

class EnhancedUploader:
    """Enhanced uploader using anasty17's techniques"""
    
    def __init__(self):
        self.max_file_size = 2 * 1024 * 1024 * 1024  # 2GB limit
        self.chunk_upload_size = 512 * 1024  # 512KB upload chunks
    
    @retry(
        wait=wait_exponential(multiplier=2, min=4, max=8),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(Exception)
    )
    async def upload_with_retry(self, update, file_path, filename, file_size):
        """Upload with retry logic like anasty17"""
        try:
            caption = f"🚀 {filename}\n📊 Size: {format_size(file_size)}\n⚡ Enhanced Speed Upload\n🔗 Source: wdzone-terabox-api"
            
            with open(file_path, 'rb') as file:
                if filename.lower().endswith(('.mp4', '.avi', '.mkv', '.mov', '.wmv')):
                    return await update.message.reply_video(
                        video=file,
                        caption=caption,
                        supports_streaming=True
                    )
                elif filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                    caption = caption.replace('🚀', '🖼️')
                    return await update.message.reply_photo(
                        photo=file,
                        caption=caption
                    )
                else:
                    caption = caption.replace('🚀', '📁')
                    return await update.message.reply_document(
                        document=file,
                        caption=caption
                    )
                    
        except Exception as e:
            LOGGER.error(f"Upload attempt failed: {e}")
            raise

async def enhanced_process_terabox_url(update: Update, url: str):
    """Enhanced processor with anasty17's techniques + fallback to simple version"""
    print(f"🚀 Starting ENHANCED Terabox processing: {url}")
    LOGGER.info(f"Starting ENHANCED Terabox processing: {url}")
    
    status_msg = await update.message.reply_text("🚀 **Enhanced Processing Mode...**", parse_mode='Markdown')
    
    try:
        # Step 1: Extract file info (same as working version)
        print(f"📋 Step 1: Using wdzone-terabox-api...")
        await status_msg.edit_text("📋 **Enhanced API Processing...**", parse_mode='Markdown')
        
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
                f"❌ **File too large!**\n\n📊 **Size:** {format_size(file_size)}\n\n**Max allowed:** 2GB", 
                parse_mode='Markdown'
            )
            return
        
        await status_msg.edit_text(
            f"📁 **File Found**\n📊 **{format_size(file_size)}**\n✅ **Enhanced Mode**\n🚀 **Multi-Connection Download...**",
            parse_mode='Markdown'
        )
        
        # Step 3: ENHANCED DOWNLOAD with anasty17's techniques
        print(f"🚀 Step 3: Enhanced multi-connection download...")
        file_path = Path(DOWNLOAD_DIR) / filename
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        
        downloader = EnhancedDownloader()
        
        async def progress_callback(downloaded, total):
            progress = (downloaded / total) * 100 if total > 0 else 0
            try:
                await status_msg.edit_text(
                    f"📁 **Enhanced Download**\n🚀 **Multi-Connection:** {progress:.1f}%\n📊 **{format_size(downloaded)} / {format_size(total)}**\n⚡ **Speed Boost Active**",
                    parse_mode='Markdown'
                )
            except:
                pass
        
        start_time = time.time()
        
        # Try enhanced multi-connection download
        try:
            if file_size > 10 * 1024 * 1024:  # Use multi-connection for files > 10MB
                await downloader.multi_connection_download(
                    download_url, 
                    file_path, 
                    file_size, 
                    progress_callback
                )
                print(f"✅ Multi-connection download completed")
            else:
                await downloader.single_connection_download(
                    download_url, 
                    file_path, 
                    progress_callback
                )
                print(f"✅ Single enhanced download completed")
                
        except Exception as download_error:
            print(f"❌ Enhanced download failed: {download_error}")
            # Fallback to simple download if enhanced fails
            if FALLBACK_AVAILABLE:
                print("🔄 Falling back to simple download method...")
                await status_msg.edit_text("🔄 **Fallback to Simple Mode...**", parse_mode='Markdown')
                return await simple_process_terabox_url(update, url)
            else:
                raise download_error
        
        download_time = time.time() - start_time
        speed = file_size / download_time / (1024 * 1024)  # MB/s
        print(f"✅ Enhanced download completed in {download_time:.1f}s at {speed:.1f} MB/s")
        
        # Step 4: ENHANCED UPLOAD with retry logic
        print(f"📤 Step 4: Enhanced upload with retry...")
        await status_msg.edit_text("📤 **Enhanced Upload with Retry...**", parse_mode='Markdown')
        
        uploader = EnhancedUploader()
        
        try:
            await uploader.upload_with_retry(update, file_path, filename, file_size)
            print(f"✅ Enhanced upload completed")
        except Exception as upload_error:
            print(f"❌ Enhanced upload failed: {upload_error}")
            await status_msg.edit_text(f"❌ **Enhanced upload failed:** {str(upload_error)}", parse_mode='Markdown')
            return
        
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
        
        total_time = time.time() - start_time
        print(f"🎉 ENHANCED process complete: {filename} in {total_time:.1f}s at {speed:.1f} MB/s!")
        LOGGER.info(f"Enhanced processing completed: {filename}")
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Enhanced process error: {error_msg}")
        LOGGER.error(f"Enhanced process error: {error_msg}")
        
        # Fallback to simple version if enhanced completely fails
        if FALLBACK_AVAILABLE:
            print("🔄 COMPLETE FALLBACK to simple processor...")
            await status_msg.edit_text("🔄 **Switching to Simple Mode...**", parse_mode='Markdown')
            return await simple_process_terabox_url(update, url)
        else:
            await status_msg.edit_text(f"❌ **Error:** {error_msg}", parse_mode='Markdown')
        
