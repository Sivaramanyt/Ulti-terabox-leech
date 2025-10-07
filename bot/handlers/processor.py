"""
Ultra Terabox Processor v2.0 - Compact Version
"""

import aiohttp
import asyncio
import os
import logging
import re
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import *

LOGGER = logging.getLogger(__name__)

TIMEOUT_CONFIG = aiohttp.ClientTimeout(total=300, connect=30, sock_read=60)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive'
}

async def process_terabox_url(update, context: ContextTypes.DEFAULT_TYPE):
    """Main Terabox processor"""
    message = update.message
    user_id = message.from_user.id
    terabox_url = message.text.strip()
    
    # Check user limits
    user_downloads = get_user_download_count(user_id)
    if user_downloads >= FREE_DOWNLOAD_LIMIT and not is_user_verified(user_id):
        await send_verification_required_message(message, user_id, user_downloads)
        return
    
    # Processing message
    status_msg = await message.reply_text("🔄 **Processing Terabox link...**", parse_mode='Markdown')
    
    try:
        # Extract file info
        file_info = await extract_terabox_info(terabox_url)
        if not file_info:
            await status_msg.edit_text("❌ **Failed to extract file info**\nTry with a valid Terabox link.")
            return
        
        filename = file_info.get('filename', 'terabox_file.mp4')
        file_size = file_info.get('size', 0)
        download_url = file_info.get('download_url', terabox_url)
        
        await status_msg.edit_text(f"⬇️ **Downloading:** `{filename}`\n📊 **Size:** {format_file_size(file_size)}")
        
        # Download file
        file_path = await download_file(download_url, filename, status_msg)
        if not file_path:
            await status_msg.edit_text("❌ **Download failed**\nTry again later.")
            return
        
        await status_msg.edit_text(f"⬆️ **Uploading:** `{filename}`")
        
        # Upload to Telegram
        await upload_file_to_telegram(message, file_path, filename, status_msg)
        
        # Cleanup
        increment_user_downloads(user_id)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        LOGGER.info(f"✅ Process complete: {filename}")
        
    except Exception as e:
        LOGGER.error(f"❌ Error: {str(e)}")
        await status_msg.edit_text(f"❌ **Error:** {str(e)}")

async def extract_terabox_info(terabox_url):
    """Extract file info from Terabox"""
    for attempt in range(3):
        try:
            async with aiohttp.ClientSession(timeout=TIMEOUT_CONFIG, headers=HEADERS) as session:
                async with session.get(terabox_url, allow_redirects=True) as response:
                    if response.status == 200:
                        content = await response.text()
                        return parse_terabox_response(content, terabox_url)
        except Exception as e:
            LOGGER.warning(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < 2:
                await asyncio.sleep(2)
    return None

def parse_terabox_response(content, original_url):
    """Parse Terabox HTML"""
    try:
        # Try JSON extraction
        json_patterns = [
            r'window\.yunData\s*=\s*({.+?});',
            r'window\.viewShareData\s*=\s*({.+?});',
            r'setData\(({.+?})\)',
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            for match in matches:
                try:
                    data = json.loads(match)
                    file_info = extract_from_json(data)
                    if file_info:
                        return file_info
                except:
                    continue
        
        # HTML extraction
        html_patterns = {
            'filename': [r'<title>([^<]+)</title>', r'data-title="([^"]+)"'],
            'size': [r'data-size="([^"]+)"', r'size["\']?\s*:\s*["\']?(\d+)'],
        }
        
        extracted = {}
        for key, patterns in html_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    extracted[key] = match.group(1)
                    break
        
        filename = clean_filename(extracted.get('filename', 'terabox_file'))
        size = int(extracted.get('size', 0)) if extracted.get('size') else 0
        
        return {
            'filename': filename,
            'size': size,
            'download_url': original_url
        }
        
    except Exception as e:
        LOGGER.error(f"Parse error: {str(e)}")
        return None

def extract_from_json(data):
    """Extract from JSON data"""
    try:
        if isinstance(data, dict):
            file_list = data.get('file_list', [])
            if file_list and len(file_list) > 0:
                item = file_list[0]
                return {
                    'filename': clean_filename(item.get('server_filename', 'terabox_file')),
                    'size': int(item.get('size', 0)),
                    'download_url': item.get('dlink', '').replace('\\/', '/')
                }
            
            filename = data.get('filename') or data.get('server_filename')
            if filename:
                return {
                    'filename': clean_filename(filename),
                    'size': int(data.get('size', 0)),
                    'download_url': data.get('dlink', '').replace('\\/', '/')
                }
    except:
        pass
    return None

def clean_filename(raw_filename):
    """Clean filename"""
    try:
        # Remove Terabox suffixes
        patterns = [
            r'\s*-\s*Share Files Online.*',
            r'\s*-\s*TeraBox.*',
            r'\s*&amp;.*'
        ]
        
        cleaned = raw_filename
        for pattern in patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Clean up
        cleaned = cleaned.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        cleaned = re.sub(r'[<>:"/\\|?*]', '', cleaned).strip()
        
        # Add extension if missing
        extensions = ['.mp4', '.avi', '.mkv', '.jpg', '.png', '.pdf', '.zip']
        if not any(cleaned.lower().endswith(ext) for ext in extensions):
            cleaned += '.mp4'
        
        return cleaned if cleaned else 'terabox_file.mp4'
    except:
        return 'terabox_file.mp4'

async def download_file(download_url, filename, status_msg=None):
    """Download file"""
    if not download_url:
        return None
    
    file_path = os.path.join(DOWNLOAD_DIR, filename)
    
    for attempt in range(3):
        try:
            async with aiohttp.ClientSession(timeout=TIMEOUT_CONFIG, headers=HEADERS) as session:
                async with session.get(download_url, allow_redirects=True) as response:
                    if response.status == 200:
                        with open(file_path, 'wb') as file:
                            async for chunk in response.content.iter_chunked(8192):
                                if chunk:
                                    file.write(chunk)
                        return file_path
        except Exception as e:
            LOGGER.warning(f"Download attempt {attempt + 1} failed: {str(e)}")
            if attempt < 2:
                await asyncio.sleep(3)
    
    return None

async def upload_file_to_telegram(message, file_path, filename, status_msg):
    """Upload to Telegram"""
    try:
        file_size = os.path.getsize(file_path)
        file_ext = filename.lower().split('.')[-1]
        
        caption = f"📁 **{filename}**\n📊 **Size:** {format_file_size(file_size)}\n✅ **Downloaded from Terabox**"
        
        if file_ext in ['mp4', 'avi', 'mkv', 'mov']:
            with open(file_path, 'rb') as video:
                await message.reply_video(video=video, caption=caption, parse_mode='Markdown')
        elif file_ext in ['jpg', 'jpeg', 'png', 'gif']:
            with open(file_path, 'rb') as photo:
                await message.reply_photo(photo=photo, caption=caption, parse_mode='Markdown')
        else:
            with open(file_path, 'rb') as doc:
                await message.reply_document(document=doc, caption=caption, parse_mode='Markdown')
        
        try:
            await status_msg.delete()
        except:
            pass
            
    except Exception as e:
        LOGGER.error(f"Upload error: {str(e)}")
        await status_msg.edit_text(f"❌ **Upload failed:** {str(e)}")

def format_file_size(size_bytes):
    """Format file size"""
    if size_bytes == 0:
        return "Unknown"
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"

# Database functions (implement as needed)
def get_user_download_count(user_id):
    return 0

def is_user_verified(user_id):
    return False

def increment_user_downloads(user_id):
    pass

async def send_verification_required_message(message, user_id, download_count):
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
        
