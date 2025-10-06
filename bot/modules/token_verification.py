"""
Simple Token Verification System - VJ Style
Exactly like the YouTube video - separate from existing code
"""

import json
import time
import random
import string
import requests
import os
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from config import LOGGER

# Get configuration from environment variables
IS_VERIFY = os.environ.get('IS_VERIFY', 'True').lower() == 'true'
FREE_LEECH_LIMIT = int(os.environ.get('FREE_LEECH_LIMIT', '3'))
VERIFY_EXPIRE = int(os.environ.get('VERIFY_EXPIRE', '3600'))  # 1 hour
SHORTLINK_API = os.environ.get('SHORTLINK_API', '')
SHORTLINK_URL = os.environ.get('SHORTLINK_URL', '')
BOT_USERNAME = os.environ.get('BOT_USERNAME', 'your_bot_username')
VERIFY_TUTORIAL = os.environ.get('VERIFY_TUTORIAL', 'https://youtu.be/7pMYsi_pcJ8')

# Database files
USER_DATA_FILE = Path("verification_users.json")
TOKEN_DATA_FILE = Path("verification_tokens.json")

class TokenVerificationSystem:
    def __init__(self):
        self.users = self.load_users()
        self.tokens = self.load_tokens()
    
    def load_users(self):
        """Load user verification data"""
        if USER_DATA_FILE.exists():
            try:
                with open(USER_DATA_FILE, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def load_tokens(self):
        """Load verification tokens"""
        if TOKEN_DATA_FILE.exists():
            try:
                with open(TOKEN_DATA_FILE, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_users(self):
        """Save user verification data"""
        try:
            with open(USER_DATA_FILE, 'w') as f:
                json.dump(self.users, f, indent=2)
        except Exception as e:
            LOGGER.error(f"Failed to save user data: {e}")
    
    def save_tokens(self):
        """Save verification tokens"""
        try:
            with open(TOKEN_DATA_FILE, 'w') as f:
                json.dump(self.tokens, f, indent=2)
        except Exception as e:
            LOGGER.error(f"Failed to save tokens: {e}")
    
    def get_user_verification_data(self, user_id):
        """Get user verification data"""
        user_id = str(user_id)
        if user_id not in self.users:
            self.users[user_id] = {
                'leech_count': 0,
                'verified_until': 0,
                'last_leech': 0,
                'total_leeches': 0,
                'username': '',
                'name': ''
            }
            self.save_users()
        return self.users[user_id]
    
    def increment_user_leech_count(self, user_id, username='', name=''):
        """Increment user's leech count"""
        user_data = self.get_user_verification_data(user_id)
        user_data['leech_count'] += 1
        user_data['total_leeches'] += 1
        user_data['last_leech'] = int(time.time())
        user_data['username'] = username or user_data.get('username', '')
        user_data['name'] = name or user_data.get('name', '')
        self.save_users()
        return user_data['leech_count']
    
    def is_verification_required(self, user_id):
        """Check if user needs verification"""
        if not IS_VERIFY:
            return False
        
        user_data = self.get_user_verification_data(user_id)
        current_time = int(time.time())
        
        # Check if user has verified access
        if user_data['verified_until'] > current_time:
            return False
        
        # Check if user exceeded free limit
        return user_data['leech_count'] >= FREE_LEECH_LIMIT
    
    def generate_verification_tokens(self, user_id):
        """Generate 3 verification tokens for user"""
        # Generate 3 random tokens (like in the YouTube video)
        tokens = []
        for i in range(3):
            token = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            tokens.append(token)
        
        # Store tokens with expiry
        token_session_id = f"verify_{user_id}_{int(time.time())}"
        current_time = int(time.time())
        
        self.tokens[token_session_id] = {
            'user_id': user_id,
            'tokens': tokens,
            'created_at': current_time,
            'expires_at': current_time + VERIFY_EXPIRE,
            'used': False
        }
        self.save_tokens()
        
        return token_session_id, tokens
    
    def create_verification_shortlink(self, verification_url):
        """Create shortlink using user's shortlink API"""
        try:
            if not SHORTLINK_API or not SHORTLINK_URL:
                LOGGER.error("Shortlink API or URL not configured")
                return None
            
            # Universal shortlink API patterns
            api_patterns = [
                f"https://{SHORTLINK_URL}/api",
                f"https://{SHORTLINK_URL}/api.php",
                f"https://{SHORTLINK_URL}/api/shorten"
            ]
            
            for api_url in api_patterns:
                try:
                    # Try GET method
                    params = {
                        'api': SHORTLINK_API,
                        'url': verification_url
                    }
                    
                    response = requests.get(api_url, params=params, timeout=10)
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            
                            # Check common response formats
                            for key in ['shortenedUrl', 'short_url', 'shorturl', 'url', 'result']:
                                if key in data and data[key]:
                                    return data[key]
                        except:
                            # Some APIs return plain text
                            if response.text.startswith('http'):
                                return response.text.strip()
                
                except Exception as e:
                    LOGGER.debug(f"API pattern failed: {e}")
                    continue
            
            LOGGER.error("All shortlink API patterns failed")
            return None
            
        except Exception as e:
            LOGGER.error(f"Shortlink generation error: {e}")
            return None
    
    def verify_user_token(self, user_id, token_input):
        """Verify user's token input"""
        current_time = int(time.time())
        
        # Clean token input
        token_input = token_input.strip()
        
        # Remove common prefixes users might add
        prefixes = ['\\redeem ', '/redeem ', 'redeem ', '\\verify ', '/verify ', 'verify ', '/start verify_']
        for prefix in prefixes:
            if token_input.lower().startswith(prefix.lower()):
                token_input = token_input[len(prefix):].strip()
                break
        
        # Find matching token
        for session_id, token_data in self.tokens.items():
            if (token_data['user_id'] == user_id and 
                not token_data['used'] and
                token_data['expires_at'] > current_time):
                
                # Check if input token matches any of the 3 generated tokens
                if token_input in token_data['tokens']:
                    # Mark session as used
                    token_data['used'] = True
                    self.save_tokens()
                    
                    # Grant verification for 24 hours
                    user_data = self.get_user_verification_data(user_id)
                    user_data['verified_until'] = current_time + (24 * 3600)  # 24 hours
                    user_data['leech_count'] = 0  # Reset counter
                    self.save_users()
                    
                    return True, "✅ Verification successful! You have 24 hours unlimited access."
        
        return False, "❌ Invalid or expired verification token."
    
    def cleanup_expired_tokens(self):
        """Remove expired tokens"""
        current_time = int(time.time())
        expired_sessions = [
            session_id for session_id, data in self.tokens.items()
            if data['expires_at'] < current_time
        ]
        
        for session_id in expired_sessions:
            del self.tokens[session_id]
        
        if expired_sessions:
            self.save_tokens()
            print(f"🧹 Cleaned up {len(expired_sessions)} expired verification tokens")

# Global verification system instance
token_verification_system = TokenVerificationSystem()

async def check_user_verification_required(update: Update, user_id: int):
    """Main function to check if user needs verification"""
    if not token_verification_system.is_verification_required(user_id):
        return True  # User can proceed with download
    
    # Generate verification tokens
    session_id, tokens = token_verification_system.generate_verification_tokens(user_id)
    
    # Create verification URL (simple telegram bot start link)
    verification_url = f"https://telegram.me/{BOT_USERNAME}?start=verify_{session_id}"
    
    # Create shortlink using user's API
    shortlink = token_verification_system.create_verification_shortlink(verification_url)
    
    if not shortlink:
        await update.message.reply_text(
            "❌ **Verification system temporarily unavailable**\n\n"
            "Please try again later or contact admin.",
            parse_mode='Markdown'
        )
        return False
    
    # Create verification message (exactly like YouTube video style)
    verification_message = f"""
🔐 **VERIFICATION REQUIRED**

You've used your **{FREE_LEECH_LIMIT} free downloads**!

**To continue downloading:**

1️⃣ **Click the verification link below**
2️⃣ **Complete the shortlink (wait 10-15 seconds)**  
3️⃣ **Copy any verification token**
4️⃣ **Send the token back to this bot**

🔗 **Verification Link:** {shortlink}

**Your Verification Tokens:**
➤ `{tokens[0]}`
➤ `{tokens[1]}`  
➤ `{tokens[2]}`

⏰ **Valid for:** 1 hour
💡 **After verification:** 24 hours unlimited downloads
📺 **Tutorial:** {VERIFY_TUTORIAL}

**Note:** Copy any ONE token above and send it to this bot after completing the link.
"""
    
    # Create inline keyboard
    keyboard = [
        [InlineKeyboardButton("🔗 Complete Verification", url=shortlink)],
        [InlineKeyboardButton("📺 How to Verify Tutorial", url=VERIFY_TUTORIAL)],
        [InlineKeyboardButton("🔄 Generate New Tokens", callback_data=f"new_tokens_{user_id}")]
    ]
    
    await update.message.reply_text(
        verification_message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )
    
    return False  # Block download until verified

async def handle_verification_token_input(update: Update, user_id: int, text: str):
    """Handle when user sends verification token"""
    success, message = token_verification_system.verify_user_token(user_id, text)
    
    if success:
        await update.message.reply_text(
            f"🎉 **VERIFICATION SUCCESSFUL!**\n\n{message}\n\n"
            "📥 **You can now send Terabox links to download files!**\n"
            "🕒 **Valid for:** 24 hours from now",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            f"❌ **VERIFICATION FAILED**\n\n{message}\n\n"
            "💡 **Try again:** Send any Terabox URL to get new verification tokens.",
            parse_mode='Markdown'
        )
    
    return success

async def handle_verification_callbacks(update, context):
    """Handle verification callback buttons"""
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("new_tokens_"):
        user_id = int(query.data.split("_")[-1])
        
        # Generate new tokens
        session_id, tokens = token_verification_system.generate_verification_tokens(user_id)
        verification_url = f"https://telegram.me/{BOT_USERNAME}?start=verify_{session_id}"
        shortlink = token_verification_system.create_verification_shortlink(verification_url)
        
        if shortlink:
            new_message = f"""
🔄 **NEW VERIFICATION TOKENS GENERATED**

🔗 **New Verification Link:** {shortlink}

**Your New Tokens:**
➤ `{tokens[0]}`
➤ `{tokens[1]}`  
➤ `{tokens[2]}`

⏰ **Valid for:** 1 hour
💡 **Complete the link above and then send any token to this bot**
"""
            await query.edit_message_text(new_message, parse_mode='Markdown')
        else:
            await query.answer("❌ Failed to generate new tokens. Try again later.", show_alert=True)

# Background cleanup task
async def verification_cleanup_task():
    """Background task to cleanup expired tokens"""
    import asyncio
    while True:
        try:
            token_verification_system.cleanup_expired_tokens()
            await asyncio.sleep(3600)  # Run every hour
        except Exception as e:
            LOGGER.error(f"Verification cleanup task error: {e}")
            await asyncio.sleep(3600)
