"""
VJ Token Verification System - Enhanced with Configurable Validity Time
Based on TechVJ Tutorial with flexible time settings
"""

import string
import secrets
import time
import requests
import asyncio
from datetime import datetime, timedelta
from config import (
    SHORTLINK_API, SHORTLINK_URL, VERIFY_TUTORIAL, BOT_USERNAME, LOGGER,
    VERIFICATION_VALIDITY_SECONDS, VALIDITY_TIME_TEXT,
    AUTO_CLEANUP_INTERVAL_HOURS, TOKEN_CLEANUP_ENABLED
)

# In-memory storage (replace with your database if needed)
verification_tokens = {}
verified_users = set()
user_download_counts = {}
user_verification_times = {}  # Track when users were verified

def generate_verification_link(user_id):
    """Generate VJ-style verification link with configurable validity"""
    try:
        # Generate random token (10 characters)
        token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(10))
        
        # Store token with user_id and configurable expiry time
        current_time = time.time()
        verification_tokens[token] = {
            'user_id': user_id,
            'created_at': current_time,
            'expires_at': current_time + VERIFICATION_VALIDITY_SECONDS
        }
        
        # Create verification URL (this will be shortened)
        verify_url = f"https://telegram.me/{BOT_USERNAME}?start=verify_{token}"
        
        # Create short link using your API
        short_link = create_short_link(verify_url)
        
        LOGGER.info(f"Generated verification link for user {user_id} (valid for {VALIDITY_TIME_TEXT})")
        return short_link
        
    except Exception as e:
        LOGGER.error(f"Error generating verification link: {e}")
        return None

def create_verification_link(user_id):
    """Alternative function name for compatibility"""
    return generate_verification_link(user_id)

def create_short_link(url):
    """Create shortlink using your configured API"""
    try:
        if not SHORTLINK_API or not SHORTLINK_URL:
            return url
        
        # Different APIs have different formats - adjust as needed
        api_url = f"{SHORTLINK_URL}/api?api={SHORTLINK_API}&url={url}"
        
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Handle different API response formats
            return data.get('shortenedUrl', data.get('shortlink', data.get('short_link', url)))
        else:
            return url
            
    except Exception as e:
        LOGGER.error(f"Shortlink API error: {e}")
        return url

def verify_user_token(token):
    """Verify token and mark user as verified with timestamp"""
    try:
        if token not in verification_tokens:
            return False, None
        
        token_data = verification_tokens[token]
        
        # Check if token expired
        if time.time() > token_data['expires_at']:
            del verification_tokens[token]
            return False, None
        
        # Mark user as verified with timestamp
        user_id = token_data['user_id']
        verified_users.add(user_id)
        user_verification_times[user_id] = time.time()
        
        # Remove used token
        del verification_tokens[token]
        
        LOGGER.info(f"User {user_id} successfully verified via token (validity: {VALIDITY_TIME_TEXT})")
        return True, user_id
        
    except Exception as e:
        LOGGER.error(f"Token verification error: {e}")
        return False, None

def check_verification(user_id):
    """Check if user is verified"""
    return user_id in verified_users

def is_user_verified(user_id):
    """Alternative function name"""
    return check_verification(user_id)

def get_user_verification_time(user_id):
    """Get when user was verified"""
    if user_id in user_verification_times:
        return user_verification_times[user_id]
    return None

def get_verification_info(user_id):
    """Get detailed verification info for user"""
    if user_id not in verified_users:
        return {
            'verified': False,
            'verification_time': None,
            'time_since_verification': None,
            'validity_remaining': None
        }
    
    verification_time = user_verification_times.get(user_id)
    if verification_time:
        time_since = time.time() - verification_time
        return {
            'verified': True,
            'verification_time': datetime.fromtimestamp(verification_time),
            'time_since_verification': time_since,
            'validity_text': VALIDITY_TIME_TEXT
        }
    
    return {
        'verified': True,
        'verification_time': None,
        'time_since_verification': None,
        'validity_text': VALIDITY_TIME_TEXT
    }

def get_user_download_count(user_id):
    """Get user download count"""
    return user_download_counts.get(user_id, 0)

def increment_user_downloads(user_id):
    """Increment user download count"""
    user_download_counts[user_id] = user_download_counts.get(user_id, 0) + 1
    LOGGER.info(f"User {user_id} download count: {user_download_counts[user_id]}")

def get_token():
    """Callback data for verification button"""
    return "start_verification"

def get_active_tokens_count():
    """Get count of active tokens"""
    current_time = time.time()
    active_count = sum(1 for data in verification_tokens.values() 
                      if current_time <= data['expires_at'])
    return active_count

def cleanup_expired_tokens():
    """Clean up expired tokens with detailed logging"""
    current_time = time.time()
    expired_tokens = []
    
    for token, data in verification_tokens.items():
        if current_time > data['expires_at']:
            expired_tokens.append(token)
    
    for token in expired_tokens:
        del verification_tokens[token]
    
    if expired_tokens:
        LOGGER.info(f"Cleaned up {len(expired_tokens)} expired tokens (validity was {VALIDITY_TIME_TEXT})")
    
    return len(expired_tokens)

def get_verification_stats():
    """Get comprehensive verification statistics"""
    active_tokens = get_active_tokens_count()
    total_verified = len(verified_users)
    
    return {
        'active_tokens': active_tokens,
        'total_verified_users': total_verified,
        'validity_time': VALIDITY_TIME_TEXT,
        'cleanup_enabled': TOKEN_CLEANUP_ENABLED,
        'cleanup_interval_hours': AUTO_CLEANUP_INTERVAL_HOURS
    }

# Auto cleanup task with configurable interval
async def auto_cleanup_task():
    """Auto cleanup expired tokens with configurable interval"""
    if not TOKEN_CLEANUP_ENABLED:
        LOGGER.info("Auto cleanup disabled")
        return
    
    cleanup_interval = AUTO_CLEANUP_INTERVAL_HOURS * 3600  # Convert to seconds
    LOGGER.info(f"Auto cleanup enabled: every {AUTO_CLEANUP_INTERVAL_HOURS} hours")
    
    while True:
        await asyncio.sleep(cleanup_interval)
        try:
            expired_count = cleanup_expired_tokens()
            if expired_count > 0:
                LOGGER.info(f"Auto cleanup completed: {expired_count} tokens removed")
        except Exception as e:
            LOGGER.error(f"Auto cleanup error: {e}")

# Time formatting utilities
def format_time_remaining(expires_at):
    """Format remaining time until expiry"""
    remaining = expires_at - time.time()
    if remaining <= 0:
        return "Expired"
    
    hours = int(remaining // 3600)
    minutes = int((remaining % 3600) // 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"

def get_token_info(token):
    """Get information about a specific token"""
    if token not in verification_tokens:
        return None
    
    data = verification_tokens[token]
    return {
        'user_id': data['user_id'],
        'created_at': datetime.fromtimestamp(data['created_at']),
        'expires_at': datetime.fromtimestamp(data['expires_at']),
        'time_remaining': format_time_remaining(data['expires_at']),
        'validity_period': VALIDITY_TIME_TEXT
    }
