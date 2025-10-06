#!/usr/bin/env python3
"""
Professional Terabox Leech Bot
Optimized for Koyeb Free Tier (512MB RAM)
Based on anasty17/mirror-leech-telegram-bot
"""

from signal import signal, SIGINT
from sys import executable
from time import time
from asyncio import run

def exit_clean_up(signal, frame):
    print("Shutting down bot gracefully...")
    exit(0)

async def main():
    from bot import bot_loop
    from bot.__main__ import main as bot_main
    
    try:
        await bot_main()
    except KeyboardInterrupt:
        print("Bot stopped by user")
    except Exception as e:
        print(f"Bot error: {e}")

if __name__ == "__main__":
    signal(SIGINT, exit_clean_up)
    print("🚀 Starting Terabox Leech Bot...")
    run(main())
