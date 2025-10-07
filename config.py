"""
Terabox Leech Bot Configuration
Optimized for minimal memory usage + Enhanced with Contact Menu & Verification System
"""

from logging import getLogger, FileHandler, StreamHandler, INFO, basicConfig
from os import environ, makedirs, path as ospath
from dotenv import load_dotenv

if ospath.exists('config.env'):
    load_dotenv('config.env', override=True)

LOGGER = getLogger(__name__)

basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[FileHandler("log.txt"), StreamHandler()],
    level=INFO,
)

# Essential Bot Configuration (ALL YOUR CURRENT CODE - UNCHANGED)
BOT_TOKEN = environ.get('BOT_TOKEN', '')
if not BOT_TOKEN:
    LOGGER.error("BOT_TOKEN is required!")
    exit(1)

TELEGRAM_API = environ.get('TELEGRAM_API', '')
if not TELEGRAM_API:
    LOGGER.error("TELEGRAM_API is required!")
    exit(1)
else:
    TELEGRAM_API = int(TELEGRAM_API)

TELEGRAM_HASH = environ.get('TELEGRAM_HASH', '')
if not TELEGRAM_HASH:
    LOGGER.error("TELEGRAM_HASH is required!")
    exit(1)

OWNER_ID = environ.get('OWNER_ID', '')
if not OWNER_ID:
    LOGGER.error("OWNER_ID is required!")
    exit(1)
else:
    OWNER_ID = int(OWNER_ID)

# Optional Configuration (ALL YOUR CURRENT CODE - UNCHANGED)
AUTHORIZED_CHATS = environ.get('AUTHORIZED_CHATS', '')
CMD_SUFFIX = environ.get('CMD_SUFFIX', '')

# Leech Configuration (ALL YOUR CURRENT CODE - UNCHANGED)
AS_DOCUMENT = environ.get('AS_DOCUMENT', 'False').lower() == 'true'
LEECH_SPLIT_SIZE = int(environ.get('LEECH_SPLIT_SIZE', '2097152000'))  # 2GB
STATUS_UPDATE_INTERVAL = int(environ.get('STATUS_UPDATE_INTERVAL', '10'))

# Download Directory (ALL YOUR CURRENT CODE - UNCHANGED)
DOWNLOAD_DIR = environ.get('DOWNLOAD_DIR', '/usr/src/app/downloads/')
if not DOWNLOAD_DIR.endswith("/"):
    DOWNLOAD_DIR = f'{DOWNLOAD_DIR}/'

# Create download directory
makedirs(DOWNLOAD_DIR, exist_ok=True)

# Memory optimization settings (ALL YOUR CURRENT CODE - UNCHANGED)
QUEUE_ALL = 2  # Limit concurrent tasks for memory efficiency
MAX_CONCURRENT_DOWNLOADS = 1  # One download at a time
MAX_CONCURRENT_UPLOADS = 1  # One upload at a time

# ✅ NEW ENHANCED FEATURES - Contact Information & Bot Settings
# UPDATE THESE WITH YOUR ACTUAL INFORMATION

# Contact Information - ✅ UPDATE THESE WITH YOUR DETAILS
DEVELOPER_CONTACT = environ.get('DEVELOPER_CONTACT', 'https://t.me/your_username')  # ✅ UPDATE THIS
UPDATES_CHANNEL = environ.get('UPDATES_CHANNEL', 'https://t.me/your_channel')       # ✅ UPDATE THIS  
SUPPORT_GROUP = environ.get('SUPPORT_GROUP', 'https://t.me/your_support_group')     # ✅ UPDATE THIS
DEVELOPER_USERNAME = environ.get('DEVELOPER_USERNAME', '@your_username')            # ✅ UPDATE THIS
DEVELOPER_EMAIL = environ.get('DEVELOPER_EMAIL', 'your_email@gmail.com')            # ✅ UPDATE THIS

# Enhanced Bot Settings
FREE_DOWNLOAD_LIMIT = int(environ.get('FREE_DOWNLOAD_LIMIT', '3'))
VERIFICATION_FALLBACK_URL = environ.get('VERIFICATION_FALLBACK_URL', 'https://your-verification-site.com/verify')  # ✅ UPDATE THIS

# Enhanced Terabox Domains (comprehensive list)
TERABOX_DOMAINS = [
    'terabox.com', 'www.terabox.com', 'teraboxapp.com', 'www.teraboxapp.com',
    '1024tera.com', 'www.1024tera.com', 'terabox.app', 'terasharelink.com',
    'nephobox.com', 'www.nephobox.com', '4funbox.com', 'www.4funbox.com',
    'mirrobox.com', 'www.mirrobox.com', 'momerybox.com', 'www.momerybox.com',
    'teraboxlink.com', 'www.teraboxlink.com', 'teraboxurl.com', 'tibibox.com'
]

# Enhanced Download Configuration
MAX_FILE_SIZE = int(environ.get('MAX_FILE_SIZE', '2147483648'))  # 2GB default
DOWNLOAD_TIMEOUT = int(environ.get('DOWNLOAD_TIMEOUT', '900'))    # 15 minutes
UPLOAD_TIMEOUT = int(environ.get('UPLOAD_TIMEOUT', '600'))        # 10 minutes

# Enhanced Status Configuration
BOT_VERSION = environ.get('BOT_VERSION', '2.0')
BOT_NAME = environ.get('BOT_NAME', 'Ultra Terabox Bot')
BOT_DESCRIPTION = environ.get('BOT_DESCRIPTION', 'Fast and reliable Terabox downloader with professional support')

# Enhanced Security Settings
ENABLE_VERIFICATION = environ.get('ENABLE_VERIFICATION', 'True').lower() == 'true'
ENABLE_RATE_LIMITING = environ.get('ENABLE_RATE_LIMITING', 'True').lower() == 'true'
MAX_DOWNLOADS_PER_DAY = int(environ.get('MAX_DOWNLOADS_PER_DAY', '50'))

# Enhanced Logging Configuration
ENABLE_DEBUG_LOGS = environ.get('ENABLE_DEBUG_LOGS', 'False').lower() == 'true'
LOG_CHAT_ID = environ.get('LOG_CHAT_ID', '')  # Optional: Chat ID for logging
if LOG_CHAT_ID:
    LOG_CHAT_ID = int(LOG_CHAT_ID)

# Enhanced Error Handling
AUTO_RETRY_DOWNLOADS = environ.get('AUTO_RETRY_DOWNLOADS', 'True').lower() == 'true'
MAX_RETRY_ATTEMPTS = int(environ.get('MAX_RETRY_ATTEMPTS', '3'))
RETRY_DELAY = int(environ.get('RETRY_DELAY', '5'))  # seconds

# Enhanced UI Configuration
SHOW_PROGRESS_BAR = environ.get('SHOW_PROGRESS_BAR', 'True').lower() == 'true'
UPDATE_PROGRESS_INTERVAL = int(environ.get('UPDATE_PROGRESS_INTERVAL', '5'))  # seconds
ENABLE_INLINE_BUTTONS = environ.get('ENABLE_INLINE_BUTTONS', 'True').lower() == 'true'

# ✅ VALIDATION AND LOGGING
def validate_config():
    """Validate configuration and log warnings for missing optional settings"""
    warnings = []
    
    # Check contact information
    if DEVELOPER_CONTACT == 'https://t.me/your_username':
        warnings.append("DEVELOPER_CONTACT not configured - using default")
    if UPDATES_CHANNEL == 'https://t.me/your_channel':
        warnings.append("UPDATES_CHANNEL not configured - using default")
    if SUPPORT_GROUP == 'https://t.me/your_support_group':
        warnings.append("SUPPORT_GROUP not configured - using default")
    if DEVELOPER_USERNAME == '@your_username':
        warnings.append("DEVELOPER_USERNAME not configured - using default")
    if DEVELOPER_EMAIL == 'your_email@gmail.com':
        warnings.append("DEVELOPER_EMAIL not configured - using default")
    
    # Log warnings
    for warning in warnings:
        LOGGER.warning(f"⚠️ {warning}")
    
    # Log successful configuration
    LOGGER.info("📋 Essential configuration validated successfully!")
    if not warnings:
        LOGGER.info("✅ All contact information configured properly!")
    else:
        LOGGER.info(f"⚠️ {len(warnings)} optional settings using defaults")

# ✅ CONFIGURATION SUMMARY
def log_config_summary():
    """Log configuration summary for debugging"""
    LOGGER.info("🚀 Bot Configuration Summary:")
    LOGGER.info(f"   📱 Bot Name: {BOT_NAME}")
    LOGGER.info(f"   🔧 Version: {BOT_VERSION}")
    LOGGER.info(f"   👤 Owner ID: {OWNER_ID}")
    LOGGER.info(f"   🔐 Verification: {'Enabled' if ENABLE_VERIFICATION else 'Disabled'}")
    LOGGER.info(f"   🆓 Free Downloads: {FREE_DOWNLOAD_LIMIT}")
    LOGGER.info(f"   📁 Download Dir: {DOWNLOAD_DIR}")
    LOGGER.info(f"   💾 Max File Size: {MAX_FILE_SIZE // (1024*1024)}MB")
    LOGGER.info(f"   ⏱️ Download Timeout: {DOWNLOAD_TIMEOUT}s")
    LOGGER.info(f"   🔄 Max Retries: {MAX_RETRY_ATTEMPTS}")
    LOGGER.info(f"   📊 Status Updates: Every {STATUS_UPDATE_INTERVAL}s")
    LOGGER.info(f"   🌐 Supported Domains: {len(TERABOX_DOMAINS)} domains")

# ✅ HELPER FUNCTIONS
def is_authorized_user(user_id):
    """Check if user is authorized"""
    if user_id == OWNER_ID:
        return True
    if AUTHORIZED_CHATS:
        authorized_ids = [int(x.strip()) for x in AUTHORIZED_CHATS.split(',') if x.strip().isdigit()]
        return user_id in authorized_ids
    return True  # Allow all users if no restrictions set

def get_download_path(filename=""):
    """Get full download path"""
    if filename:
        return ospath.join(DOWNLOAD_DIR, filename)
    return DOWNLOAD_DIR

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"

# ✅ RUN VALIDATION AND LOGGING
validate_config()
log_config_summary()

LOGGER.info("Configuration loaded successfully!")
LOGGER.info("🎯 Ready for enhanced Terabox processing with professional contact system!")
