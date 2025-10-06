"""
Direct file downloader optimized for memory efficiency
"""

import aiohttp
import aiofiles
from pathlib import Path
from config import DOWNLOAD_DIR, LOGGER
from ..telegram_helper.message_utils import editMessage

class DirectDownloader:
    def __init__(self):
        self.session = None
    
    async def download_file(self, url, filename, message, status_msg):
        """Download file from direct URL"""
        try:
            file_path = Path(DOWNLOAD_DIR) / filename
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        total_size = int(response.headers.get('content-length', 0))
                        downloaded = 0
                        
                        async with aiofiles.open(file_path, 'wb') as f:
                            async for chunk in response.content.iter_chunked(8192):
                                await f.write(chunk)
                                downloaded += len(chunk)
                                
                                # Update progress every 1MB
                                if downloaded % (1024 * 1024) == 0:
                                    if total_size > 0:
                                        progress = (downloaded / total_size) * 100
                                        await editMessage(status_msg, 
                                            f"📁 **File:** `{filename}`\n"
                                            f"⬇️ **Downloading:** {progress:.1f}%"
                                        )
                        
                        return str(file_path)
                    else:
                        raise Exception(f"HTTP {response.status}")
                        
        except Exception as e:
            LOGGER.error(f"Download error: {e}")
            return None
