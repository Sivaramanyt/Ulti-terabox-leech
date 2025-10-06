"""
Terabox Leech Bot Configuration
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
MAX_CONCURRENT_UPLOADS = 1    # One upload at a time

LOGGER.info("Configuration loaded successfully!")
