"""
Token Verification System for Ultra Terabox Bot
Simple working verification system
"""

import secrets
import time
from config import LOGGER

# Simple in-memory storage (for basic functionality)
verification_tokens = {}
verified_users = set()

def generate_verification_link(user_id):
    """Generate verification link for user"""
    try:
        # Generate unique token
        token = secrets.token_urlsafe(16)
        
        # Store token with expiry (24 hours)
        verification_tokens[token] = {
            'user_id': user_id,
            'created_at': time.time(),
            'expires_at': time.time() + (24 * 60 * 60)  # 24 hours
        }
        
        # Create verification link
        verification_link = f"https://earnl.xyz/ref/sivaramanyt?wsa={token}"
        
        LOGGER.info(f"Generated verification link for user {user_id}: {verification_link}")
        return verification_link
        
    except Exception as e:
        LOGGER.error(f"Error generating verification link: {e}")
        return None

def create_verification_link(user_id):
    """Alternative function name (for compatibility)"""
    return generate_verification_link(user_id)

def verify_token(token):
    """Verify if token is valid and mark user as verified"""
    try:
        if token not in verification_tokens:
            return False, "Invalid token"
        
        token_data = verification_tokens[token]
        
        # Check if token expired
        if time.time() > token_data['expires_at']:
            del verification_tokens[token]
            return False, "Token expired"
        
        # Mark user as verified
        user_id = token_data['user_id']
        verified_users.add(user_id)
        
        # Remove used token
        del verification_tokens[token]
        
        LOGGER.info(f"User {user_id} successfully verified")
        return True, f"User {user_id} verified successfully"
        
    except Exception as e:
        LOGGER.error(f"Error verifying token: {e}")
        return False, "Verification error"

def is_user_verified(user_id):
    """Check if user is verified"""
    return user_id in verified_users

def add_verified_user(user_id):
    """Manually add verified user"""
    verified_users.add(user_id)
    LOGGER.info(f"User {user_id} manually verified")

def remove_verified_user(user_id):
    """Remove verified user"""
    if user_id in verified_users:
        verified_users.remove(user_id)
        LOGGER.info(f"User {user_id} verification removed")

def get_verification_stats():
    """Get verification statistics"""
    active_tokens = len(verification_tokens)
    verified_count = len(verified_users)
    
    return {
        'active_tokens': active_tokens,
        'verified_users': verified_count,
        'total_verified': verified_count
    }

def cleanup_expired_tokens():
    """Clean up expired tokens"""
    current_time = time.time()
    expired_tokens = []
    
    for token, data in verification_tokens.items():
        if current_time > data['expires_at']:
            expired_tokens.append(token)
    
    for token in expired_tokens:
        del verification_tokens[token]
    
    if expired_tokens:
        LOGGER.info(f"Cleaned up {len(expired_tokens)} expired tokens")
    
    return len(expired_tokens)
        
