"""
Auto-Forward System for Private Channel
Forwards all successful downloads to your private channel
"""

import os
import asyncio
from datetime import datetime
from telegram.error import TelegramError
from config import LOGGER

# Configuration from environment
AUTO_FORWARD_ENABLED = os.environ.get('AUTO_FORWARD', 'True').lower() == 'true'
LOG_CHANNEL_ID = int(os.environ.get('LOG_CHANNEL', '0'))

class AutoForwardSystem:
    def __init__(self, bot):
        self.bot = bot
        self.log_channel = LOG_CHANNEL_ID
        self.enabled = AUTO_FORWARD_ENABLED and LOG_CHANNEL_ID != 0
    
    async def forward_user_file(self, message, user_id, user_name, username, file_type):
        """Forward user's file to private channel"""
        if not self.enabled:
            return False
        
        try:
            # Forward the original message
            forwarded_msg = await message.forward(self.log_channel)
            
            # Send user info as reply
            user_info_text = f"""
👤 **User Information:**
🆔 **ID:** `{user_id}`
👤 **Name:** {user_name}
📱 **Username:** @{username if username else 'None'}
🎯 **File Type:** {file_type.title()}
🕒 **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📊 **Total Downloads:** {self._get_user_total_downloads(user_id)}
"""
            
            await self.bot.send_message(
                self.log_channel,
                user_info_text,
                parse_mode='Markdown',
                reply_to_message_id=forwarded_msg.message_id
            )
            
            LOGGER.info(f"File forwarded to channel for user {user_id}")
            return True
        
        except TelegramError as e:
            LOGGER.error(f"Failed to forward file for user {user_id}: {e}")
            
            # Try to send error notification
            try:
                error_text = f"⚠️ **Forward Failed**\nUser: {user_name} ({user_id})\nError: {str(e)}"
                await self.bot.send_message(self.log_channel, error_text, parse_mode='Markdown')
            except:
                pass
            
            return False
        except Exception as e:
            LOGGER.error(f"Unexpected error forwarding file: {e}")
            return False
    
    def _get_user_total_downloads(self, user_id):
        """Get user's total download count"""
        try:
            from .token_verification import token_verification_system
            user_data = token_verification_system.get_user_verification_data(user_id)
            return user_data.get('total_leeches', 0)
        except:
            return 0

# Global auto-forward instance
auto_forward_system = None

def initialize_auto_forward(bot):
    """Initialize auto-forward system with bot instance"""
    global auto_forward_system
    auto_forward_system = AutoForwardSystem(bot)
    return auto_forward_system

async def auto_forward_user_file(message, user_id, user_name, username, file_type):
    """Helper function to forward user's file"""
    if auto_forward_system:
        return await auto_forward_system.forward_user_file(message, user_id, user_name, username, file_type)
    return False
