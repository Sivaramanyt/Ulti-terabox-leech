from asyncio import new_event_loop, set_event_loop
from logging import getLogger
from time import time

# Create event loop
bot_loop = new_event_loop()
set_event_loop(bot_loop)

LOGGER = getLogger(__name__)
bot_start_time = time()

# Download directory
DOWNLOAD_DIR = "/usr/src/app/downloads/"

# Initialize bot
LOGGER.info("Bot package initialized")
