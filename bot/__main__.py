"""
Enhanced Main File - SAFE Approach (RECOMMENDED)
ALL your existing MLTB code preserved + verification runs independently
"""

# ALL YOUR EXISTING MLTB IMPORTS (keep exactly as they are)
from . import LOGGER, bot_loop

from .core.mltb_client import TgClient

from .core.config_manager import Config

Config.load()

# ALL YOUR EXISTING MAIN FUNCTION (completely untouched)
async def main():
    from asyncio import gather

    from .core.startup import (
        load_settings,
        load_configurations,
        save_settings,
        update_aria2_options,
        update_nzb_options,
        update_qb_options,
        update_variables,
    )

    await load_settings()
    await gather(TgClient.start_bot(), TgClient.start_user())
    await gather(load_configurations(), update_variables())

    from .core.torrent_manager import TorrentManager

    await TorrentManager.initiate()
    await gather(
        update_qb_options(),
        update_aria2_options(),
        update_nzb_options(),
    )

    from .helper.ext_utils.files_utils import clean_all
    from .core.jdownloader_booter import jdownloader
    from .helper.ext_utils.telegraph_helper import telegraph
    from .helper.mirror_leech_utils.rclone_utils.serve import rclone_serve_booter
    from .modules import (
        initiate_search_tools,
        get_packages_version,
        restart_notification,
    )

    await gather(
        save_settings(),
        jdownloader.boot(),
        clean_all(),
        initiate_search_tools(),
        get_packages_version(),
        restart_notification(),
        telegraph.create_account(),
        rclone_serve_booter(),
    )

# ALL YOUR EXISTING BOT STARTUP (completely untouched)
bot_loop.run_until_complete(main())

from .helper.ext_utils.bot_utils import create_help_buttons
from .helper.listeners.aria2_listener import add_aria2_callbacks
from .core.handlers import add_handlers

add_aria2_callbacks()
create_help_buttons()
add_handlers()

# ========================
# NEW: VERIFICATION SYSTEM (Independent - doesn't affect existing code)
# ========================

async def start_verification_system_safely():
    """
    Start verification system independently and safely
    If it fails, main bot continues working normally
    """
    import os
    
    # Only start if verification is enabled
    if os.environ.get('IS_VERIFY', 'False').lower() != 'true':
        LOGGER.info("ℹ️  Token verification system is DISABLED")
        return
    
    try:
        LOGGER.info("🔐 Starting token verification system...")
        
        # Import verification modules
        from .modules.token_verification import verification_cleanup_task
        
        # Start cleanup task
        await verification_cleanup_task()
        LOGGER.info("✅ Token verification cleanup task started successfully")
        
    except ImportError as e:
        LOGGER.warning(f"⚠️  Verification modules not found: {e}")
        LOGGER.info("ℹ️  Bot will continue working without verification")
        
    except Exception as e:
        LOGGER.error(f"❌ Failed to start verification system: {e}")
        LOGGER.info("ℹ️  Bot will continue working without verification")

# NEW: Start verification system in background (safe)
import asyncio
import os

# Only create task if verification is enabled
if os.environ.get('IS_VERIFY', 'False').lower() == 'true':
    try:
        # Start verification system asynchronously
        asyncio.create_task(start_verification_system_safely())
        LOGGER.info("🚀 Verification system task created")
    except Exception as e:
        LOGGER.error(f"❌ Failed to create verification task: {e}")
        LOGGER.info("ℹ️  Bot will continue without verification")
else:
    LOGGER.info("ℹ️  Verification system disabled by configuration")

# ALL YOUR EXISTING BOT FINAL STARTUP (completely untouched)
LOGGER.info("Bot Started!")

# NEW: Log current configuration status
LOGGER.info("🔐 Enhanced MLTB with Token Verification Support")
LOGGER.info(f"📊 Verification Status: {'ENABLED' if os.environ.get('IS_VERIFY', 'False').lower() == 'true' else 'DISABLED'}")

bot_loop.run_forever()
    
