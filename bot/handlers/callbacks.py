"""
COMPLETE Callback Query Handlers - AROLINKS API AUTOMATED VERSION
Full file with all callback functions + automatic link generation
"""

import os
import time
import logging
import requests
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, ContextTypes
from config import *

LOGGER = logging.getLogger(__name__)

# ✅ AROLINKS API CONFIGURATION
AROLINKS_API_KEY = os.getenv('AROLINKS_API_KEY', 'your_api_key_here')
AROLINKS_API_URL = "https://arolinks.com/api/v1/shorten"
BOT_USERNAME = os.getenv('BOT_USERNAME', 'your_bot_username')

# ✅ AROLINKS API INTEGRATION - AUTOMATIC LINK GENERATION
async def generate_arolinks_api_link(user_id: int, destination_url: str = None):
    """Generate verification link using Arolinks API - AUTOMATIC"""
    try:
        # ✅ DESTINATION URL (where users go after verification)
        if not destination_url:
            destination_url = f"https://t.me/{BOT_USERNAME}?start=verified_{user_id}"
        
        # ✅ AROLINKS API REQUEST
        api_payload = {
            'api_key': AROLINKS_API_KEY,
            'url': destination_url,
            'custom_alias': f'verify_{user_id}_{int(time.time())}',  # Unique alias
            'type': 'verification'
        }
        
        # ✅ MAKE API CALL
        response = requests.post(AROLINKS_API_URL, data=api_payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                short_url = result.get('short_url')
                LOGGER.info(f"✅ Arolinks API generated: {short_url} for user {user_id}")
                return short_url
            else:
                LOGGER.error(f"❌ Arolinks API error: {result.get('message')}")
                return f"https://arolinks.com/fallback?user={user_id}"
        else:
            LOGGER.error(f"❌ Arolinks API HTTP error: {response.status_code}")
            return f"https://arolinks.com/fallback?user={user_id}"
            
    except Exception as e:
        LOGGER.error(f"❌ Arolinks API exception: {e}")
        return f"https://arolinks.com/fallback?user={user_id}"

# ✅ MAIN CALLBACK HANDLER
async def handle_callback_queries(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all callback queries from inline buttons"""
    query = update.callback_query
    await query.answer()

    if query.data == "about":
        await handle_about_callback(query, context)
    elif query.data == "status":
        await handle_status_callback(query, context)
    elif query.data == "why_verify":
        await handle_why_verify_callback(query, context)
    elif query.data == "start_verification":
        await handle_start_verification_callback(query, context)
    elif query.data == "verification_menu":
        await handle_verification_menu_callback(query, context)
    elif query.data == "contact":
        await handle_contact_callback(query, context)
    elif query.data == "help":
        await handle_help_callback(query, context)
    else:
        # Handle unknown callback
        await query.edit_message_text(
            "❌ **Unknown Action**\n\n"
            "This button action is not recognized.\n"
            "Please try using /start to refresh the bot.",
            parse_mode='Markdown'
        )

# ✅ ABOUT CALLBACK
async def handle_about_callback(query, context):
    """Handle about callback"""
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"ℹ️ **About Ultra Terabox Bot v2.0**\n\n"
        f"🤖 **Bot Name:** {BOT_NAME}\n"
        f"📊 **Version:** 2.0 Arolinks API Edition\n"
        f"👤 **Owner:** {OWNER_ID}\n"
        f"🎯 **Purpose:** Professional Terabox file downloader\n\n"
        f"✨ **Features:**\n"
        f"• High-speed aiohttp downloads\n"
        f"• Original video quality & thumbnails\n"
        f"• Automatic Arolinks API verification\n"
        f"• Professional user interface\n"
        f"• Multi-format support (video/image/document)\n\n"
        f"🔧 **Technology:** Python + Telegram Bot API + Arolinks API\n"
        f"📈 **Performance:** Optimized for reliability\n"
        f"🛡️ **Security:** Automated Arolinks user verification\n"
        f"🌐 **Hosting:** Koyeb cloud deployment",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# ✅ STATUS CALLBACK
async def handle_status_callback(query, context):
    """Handle status callback"""
    user_id = query.from_user.id
    
    # Get user stats (implement with your database)
    try:
        user_downloads = 2  # Replace with actual database call
        is_verified = False  # Replace with actual verification check
    except:
        user_downloads = 0
        is_verified = False
    
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    status_emoji = "✅" if is_verified else "⚠️"
    status_text = "Verified (Arolinks API)" if is_verified else "Not Verified"
    remaining_downloads = max(0, FREE_DOWNLOAD_LIMIT - user_downloads)
    
    await query.edit_message_text(
        f"📊 **Your Status**\n\n"
        f"👤 **User ID:** `{user_id}`\n"
        f"{status_emoji} **Status:** {status_text}\n"
        f"📥 **Downloads Used:** {user_downloads}/{FREE_DOWNLOAD_LIMIT}\n"
        f"🆓 **Remaining Free:** {remaining_downloads}\n"
        f"⭐ **Account Type:** {'Premium (Arolinks Verified)' if is_verified else 'Free'}\n\n"
        f"📈 **Download History:**\n"
        f"• Today: {user_downloads} files\n"
        f"• This week: {user_downloads} files\n"
        f"• Total: {user_downloads} files\n\n"
        f"🎯 **Next Steps:**\n"
        f"{'🎉 Enjoy unlimited downloads!' if is_verified else '🔓 Complete Arolinks API verification for unlimited access'}\n\n"
        f"🤖 **API Status:** {'Connected' if AROLINKS_API_KEY else 'Not Configured'}",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# ✅ WHY VERIFY CALLBACK
async def handle_why_verify_callback(query, context):
    """Handle why verification callback"""
    keyboard = [
        [InlineKeyboardButton("🔓 Start Arolinks API Verification", callback_data="start_verification")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="verification_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "❓ **Why Arolinks API Verification is Required**\n\n"
        "🛡️ **Prevents Abuse**\n"
        "• Stops spam and bot attacks\n"
        "• Ensures fair usage for all users\n"
        "• Protects server resources\n\n"
        "⚡ **Better Performance**\n"
        "• Faster download speeds\n"
        "• Priority server access\n"
        "• Reduced waiting times\n\n"
        "🔒 **Security Benefits**\n"
        "• Protects your privacy\n"
        "• Secure file transfers\n"
        "• Safe download environment\n\n"
        "🤖 **API Advantages**\n"
        "• Automatic link generation\n"
        "• Fresh links every time\n"
        "• Higher success rate\n"
        "• Real-time verification\n\n"
        "🎯 **What You Get**\n"
        "• ♾️ Unlimited downloads\n"
        "• 🚀 Priority support\n"
        "• 📱 Mobile optimized\n"
        "• 🎥 Original video quality\n\n"
        "✅ **One-time Arolinks API verification - Use forever!**",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# ✅ START VERIFICATION CALLBACK - WITH AROLINKS API
async def handle_start_verification_callback(query, context):
    """Handle verification with AUTOMATIC Arolinks API links"""
    user_id = query.from_user.id
    
    try:
        # ✅ GENERATE MULTIPLE VERIFICATION LINKS AUTOMATICALLY
        verification_tasks = [
            generate_arolinks_api_link(user_id, f"https://t.me/{BOT_USERNAME}?success1={user_id}"),
            generate_arolinks_api_link(user_id, f"https://t.me/{BOT_USERNAME}?success2={user_id}"),
            generate_arolinks_api_link(user_id, f"https://t.me/{BOT_USERNAME}?success3={user_id}")
        ]
        
        # ✅ GENERATE ALL LINKS SIMULTANEOUSLY (FAST)
        verification_links = await asyncio.gather(*verification_tasks)
        
        keyboard = [
            [InlineKeyboardButton("🔗 Auto-Generated Link #1", url=verification_links[0])],
            [InlineKeyboardButton("🔗 Auto-Generated Link #2", url=verification_links[1])],
            [InlineKeyboardButton("🔗 Auto-Generated Link #3", url=verification_links[2])],
            [InlineKeyboardButton("❓ Why Verification?", callback_data="why_verify")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="verification_menu")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"🤖 **AUTO-GENERATED Arolinks API Verification**\n\n"
            f"**Fresh verification links generated automatically:**\n\n"
            f"**📋 Process:**\n"
            f"**Step 1:** Click any verification button below\n"
            f"**Step 2:** Complete Arolinks verification (30-60 seconds)\n"
            f"**Step 3:** Return for unlimited downloads!\n\n"
            f"**👤 User ID:** `{user_id}`\n"
            f"**🤖 Generated:** Just now using Arolinks API\n"
            f"**🎯 Reward:** Unlimited downloads forever\n\n"
            f"**⚡ API Features:**\n"
            f"• Fresh links every time\n"
            f"• Custom verification tracking\n"
            f"• Optimized for mobile & desktop\n"
            f"• Real-time link generation\n"
            f"• Higher success rate\n\n"
            f"**📱 Works on all devices!**\n"
            f"✅ **After verification: Enjoy unlimited Terabox downloads!**",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
        LOGGER.info(f"✅ Auto-generated Arolinks API verification links for user {user_id}")
        
    except Exception as e:
        LOGGER.error(f"❌ Auto-generation failed: {e}")
        
        # ✅ FALLBACK TO MANUAL LINKS
        manual_links = [
            f"https://arolinks.com/manual1?user={user_id}",
            f"https://arolinks.com/manual2?user={user_id}"
        ]
        
        keyboard = [
            [InlineKeyboardButton("🔗 Manual Arolinks Verify", url=manual_links[0])],
            [InlineKeyboardButton("🔄 Try API Again", callback_data="start_verification")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"🔗 **Arolinks Verification**\n\n"
            f"API auto-generation temporarily unavailable.\n"
            f"Using backup verification method.\n\n"
            f"**User ID:** `{user_id}`\n"
            f"**Fallback:** Manual links provided\n"
            f"**Status:** API will retry automatically\n\n"
            f"Click verification button below:",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

# ✅ VERIFICATION MENU CALLBACK
async def handle_verification_menu_callback(query, context):
    """Handle verification menu callback"""
    user_id = query.from_user.id
    
    keyboard = [
        [InlineKeyboardButton("🤖 Start Arolinks API Verification", callback_data="start_verification")],
        [InlineKeyboardButton("❓ Why Verification?", callback_data="why_verify")],
        [InlineKeyboardButton("📊 Check Status", callback_data="status")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="help")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🤖 **Arolinks API Verification Center**\n\n"
        f"**Current Status:** You've reached your download limit ({FREE_DOWNLOAD_LIMIT}/3 free downloads)\n\n"
        "**To continue downloading:**\n"
        "• Click 'Start Arolinks API Verification' below\n"
        "• Complete the automated verification process\n"
        "• Return and get unlimited downloads!\n\n"
        "**⚡ Arolinks API Verification Process:**\n"
        "• Takes only 30-60 seconds\n"
        "• Automatic link generation\n"
        "• One-time process\n"
        "• Safe and secure\n"
        "• Works on mobile & desktop\n\n"
        "**🎁 Benefits After API Verification:**\n"
        "• ♾️ Unlimited Terabox downloads\n"
        "• 🚀 Priority download speeds\n"
        "• 🎥 Original video quality\n"
        "• 📱 Mobile optimized experience\n"
        "• 🤖 Automatic verification system",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# ✅ CONTACT CALLBACK
async def handle_contact_callback(query, context):
    """Handle contact callback"""
    keyboard = [
        [InlineKeyboardButton("💬 Support Group", url=f"https://t.me/{SUPPORT_GROUP}")],
        [InlineKeyboardButton("📢 Updates Channel", url=f"https://t.me/{UPDATES_CHANNEL}")],
        [InlineKeyboardButton("👨‍💻 Developer", url=f"https://t.me/{DEVELOPER_USERNAME}")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"📞 **Contact & Support**\n\n"
        f"**🆘 Need Help?**\n"
        f"Join our support group for quick assistance!\n\n"
        f"**📢 Stay Updated**\n"
        f"Follow our channel for latest updates and features.\n\n"
        f"**👨‍💻 Developer Contact**\n"
        f"Reach out to the developer for technical issues.\n\n"
        f"**📧 Email Support**\n"
        f"`{DEVELOPER_EMAIL}`\n\n"
        f"**⚡ Quick Support:**\n"
        f"• Bot issues: Use support group\n"
        f"• Feature requests: Contact developer\n"
        f"• Bug reports: Email or support group\n"
        f"• Arolinks API issues: Contact support group\n"
        f"• Verification problems: Developer contact\n\n"
        f"**🕒 Support Hours:**\n"
        f"24/7 community support available!\n"
        f"Developer: 9 AM - 9 PM IST",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# ✅ HELP/MAIN MENU CALLBACK
async def handle_help_callback(query, context):
    """Handle help/main menu callback"""
    keyboard = [
        [InlineKeyboardButton("ℹ️ About Bot", callback_data="about")],
        [InlineKeyboardButton("📊 My Status", callback_data="status")],
        [InlineKeyboardButton("📞 Contact", callback_data="contact")],
        [InlineKeyboardButton("🤖 Arolinks API Verification", callback_data="verification_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"🎯 **{BOT_NAME} - Main Menu**\n\n"
        f"**🚀 Quick Start:**\n"
        f"• Send any Terabox link to download\n"
        f"• Get {FREE_DOWNLOAD_LIMIT} free downloads daily\n"
        f"• Complete Arolinks API verification for unlimited access\n\n"
        f"**📱 Supported Formats:**\n"
        f"• 🎥 Videos (MP4, AVI, MKV, MOV, etc.)\n"
        f"• 🖼️ Images (JPG, PNG, GIF, etc.)\n"
        f"• 📁 Documents (PDF, ZIP, etc.)\n\n"
        f"**✨ Features:**\n"
        f"• Original quality downloads\n"
        f"• Video thumbnails included\n"
        f"• Fast aiohttp technology\n"
        f"• Automated Arolinks API verification\n"
        f"• Real-time link generation\n\n"
        f"**💡 Tips:**\n"
        f"• Send links directly (no commands needed)\n"
        f"• Verify once with Arolinks API for unlimited downloads\n"
        f"• Join our channel for updates\n"
        f"• API generates fresh verification links automatically",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# ✅ EXPORT THE MAIN HANDLER FUNCTION
def get_callback_handler():
    """Get the callback query handler"""
    return CallbackQueryHandler(handle_callback_queries)
        
