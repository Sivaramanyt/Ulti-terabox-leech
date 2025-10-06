"""
Telegram uploader optimized for memory efficiency
"""

from pyrogram.types import Message
from pathlib import Path
from config import LEECH_SPLIT_SIZE, AS_DOCUMENT, LOGGER
from ...telegram_helper.message_utils import editMessage
from ....core.tg_client import TgClient

class TelegramUploader:
    def __init__(self):
        pass
    
    async def upload_file(self, file_path, message: Message, status_msg):
        """Upload file to Telegram"""
        try:
            file_path = Path(file_path)
            file_size = file_path.stat().st_size
            filename = file_path.name
            
            # Check if file needs splitting
            if file_size > LEECH_SPLIT_SIZE:
                await editMessage(status_msg, "❌ **File too large for splitting in this version**")
                return
            
            # Upload single file
            await self._upload_single_file(file_path, message, status_msg)
            
        except Exception as e:
            LOGGER.error(f"Upload error: {e}")
            await editMessage(status_msg, f"❌ **Upload failed:** {str(e)}")
    
    async def _upload_single_file(self, file_path, message: Message, status_msg):
        """Upload single file"""
        filename = file_path.name
        
        try:
            if AS_DOCUMENT or not self._is_media_file(filename):
                # Upload as document
                await TgClient.bot.send_document(
                    chat_id=message.chat.id,
                    document=str(file_path),
                    caption=f"📁 **{filename}**",
                    reply_to_message_id=message.id,
                    progress=self._progress_callback,
                    progress_args=(status_msg, filename, "📤 **Uploading:**")
                )
            else:
                # Upload as media based on file type
                if filename.lower().endswith(('.mp4', '.avi', '.mkv', '.mov', '.wmv')):
                    await TgClient.bot.send_video(
                        chat_id=message.chat.id,
                        video=str(file_path),
                        caption=f"🎥 **{filename}**",
                        reply_to_message_id=message.id,
                        progress=self._progress_callback,
                        progress_args=(status_msg, filename, "📤 **Uploading:**")
                    )
                else:
                    await TgClient.bot.send_document(
                        chat_id=message.chat.id,
                        document=str(file_path),
                        caption=f"📁 **{filename}**",
                        reply_to_message_id=message.id,
                        progress=self._progress_callback,
                        progress_args=(status_msg, filename, "📤 **Uploading:**")
                    )
                    
        except Exception as e:
            LOGGER.error(f"Single file upload error: {e}")
            raise
    
    async def _progress_callback(self, current, total, status_msg, filename, prefix):
        """Progress callback for uploads"""
        try:
            progress = (current / total) * 100
            await editMessage(status_msg, 
                f"📁 **File:** `{filename}`\n"
                f"{prefix} {progress:.1f}%"
            )
        except:
            pass  # Ignore progress update errors
    
    def _is_media_file(self, filename):
        """Check if file is a media file"""
        media_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm',
                          '.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a',
                          '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        
        return Path(filename).suffix.lower() in media_extensions
            
