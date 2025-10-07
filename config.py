"""
Terabox Leech Bot Configuration - Enhanced with VJ Verification & Validity Time
Optimized for minimal memory usage
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

# Essential Bot Configuration
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

# Optional Configuration
AUTHORIZED_CHATS = environ.get('AUTHORIZED_CHATS', '')
CMD_SUFFIX = environ.get('CMD_SUFFIX', '')

# Leech Configuration
AS_DOCUMENT = environ.get('AS_DOCUMENT', 'False').lower() == 'true'
LEECH_SPLIT_SIZE = int(environ.get('LEECH_SPLIT_SIZE', '2097152000'))  # 2GB
STATUS_UPDATE_INTERVAL = int(environ.get('STATUS_UPDATE_INTERVAL', '10'))

# Download Directory
DOWNLOAD_DIR = environ.get('DOWNLOAD_DIR', '/usr/src/app/downloads/')
if not DOWNLOAD_DIR.endswith("/"):
    DOWNLOAD_DIR = f'{DOWNLOAD_DIR}/'

# Create download directory
makedirs(DOWNLOAD_DIR, exist_ok=True)

# Memory optimization settings
QUEUE_ALL = 2  # Limit concurrent tasks for memory efficiency
MAX_CONCURRENT_DOWNLOADS = 1  # One download at a time
MAX_CONCURRENT_UPLOADS = 1  # One upload at a time

# ✅ VJ VERIFICATION SYSTEM SETTINGS (ENHANCED WITH VALIDITY TIME)
BOT_USERNAME = environ.get('BOT_USERNAME', '').replace('@', '')
SHORTLINK_API = environ.get('SHORTLINK_API', '')
SHORTLINK_URL = environ.get('SHORTLINK_URL', '')
VERIFY_TUTORIAL = environ.get('VERIFY_TUTORIAL', 'https://t.me/your_tutorial_channel')
VERIFY = environ.get('VERIFY', 'True').lower() == 'true'
FREE_DOWNLOAD_LIMIT = int(environ.get('FREE_DOWNLOAD_LIMIT', '3'))

# 🕐 VERIFICATION VALIDITY TIME SETTINGS (NEW)
VERIFICATION_VALIDITY_HOURS = int(environ.get('VERIFICATION_VALIDITY_HOURS', '24'))  # Default 24 hours
VERIFICATION_VALIDITY_MINUTES = int(environ.get('VERIFICATION_VALIDITY_MINUTES', '0'))  # Additional minutes
VERIFICATION_VALIDITY_SECONDS = VERIFICATION_VALIDITY_HOURS * 3600 + VERIFICATION_VALIDITY_MINUTES * 60

# Token cleanup settings
AUTO_CLEANUP_INTERVAL_HOURS = int(environ.get('AUTO_CLEANUP_INTERVAL_HOURS', '1'))  # Cleanup every hour
TOKEN_CLEANUP_ENABLED = environ.get('TOKEN_CLEANUP_ENABLED', 'True').lower() == 'true'

# Support and Developer Info
DEVELOPER_USERNAME = environ.get('DEVELOPER_USERNAME', '@YourUsername')
SUPPORT_GROUP = environ.get('SUPPORT_GROUP', 'https://t.me/your_support_group')
VERIFICATION_FALLBACK_URL = environ.get('VERIFICATION_FALLBACK_URL', 'https://earnl.xyz/ref/sivaramanyt')

# Time formatting for user display
def get_validity_time_text():
    """Get human-readable validity time text"""
    if VERIFICATION_VALIDITY_HOURS >= 24:
        days = VERIFICATION_VALIDITY_HOURS // 24
        remaining_hours = VERIFICATION_VALIDITY_HOURS % 24
        if days == 1 and remaining_hours == 0:
            return "24 hours"
        elif remaining_hours == 0:
            return f"{days} days"
        else:
            return f"{days} days {remaining_hours} hours"
    elif VERIFICATION_VALIDITY_HOURS > 0:
        if VERIFICATION_VALIDITY_MINUTES > 0:
            return f"{VERIFICATION_VALIDITY_HOURS} hours {VERIFICATION_VALIDITY_MINUTES} minutes"
        else:
            return f"{VERIFICATION_VALIDITY_HOURS} hours"
    else:
        return f"{VERIFICATION_VALIDITY_MINUTES} minutes"

VALIDITY_TIME_TEXT = get_validity_time_text()

LOGGER.info(f"✅ Configuration loaded successfully with VJ Verification!")
LOGGER.info(f"🕐 Verification validity time: {VALIDITY_TIME_TEXT}")
