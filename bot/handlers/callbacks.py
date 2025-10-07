"""
Callback Query Handlers for Inline Buttons - ENHANCED VERSION
Fixed verification system with working button handlers
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, ContextTypes
from config import *

LOGGER = logging.getLogger(__name__)

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

async def handle_about_callback(query, context):
    """Handle about callback"""
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"ℹ️ **About Ultra Terabox Bot v2.0**\n\n"
        f"🤖 **Bot Name:** {BOT_NAME}\n"
        f"📊 **Version:** 2.0 Enhanced Edition\n"
        f"👤 **Owner:** {OWNER_ID}\n"
        f"🎯 **Purpose:** Professional Terabox file downloader\n\n"
        f"✨ **Features:**\n"
        f"• High-speed micro-chunk downloads\n"
        f"• Original video quality & thumbnails\n"
        f"• Advanced verification system\n"
        f"• Professional user interface\n"
        f"• Multi-format support (video/image/document)\n\n"
        f"🔧 **Technology:** Python + Telegram Bot API\n"
        f"📈 **Performance:** Optimized for reliability\n"
        f"🛡️ **Security:** Advanced user verification",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_status_callback(query, context):
    """Handle status callback"""
    user_id = query.from_user.id
    
    # Get user stats (you can implement this based on your database)
    try:
        # This is a placeholder - replace with your actual database call
        user_downloads = 2  # Replace with actual download count
        is_verified = False  # Replace with actual verification status
    except:
        user_downloads = 0
        is_verified = False
    
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    status_emoji = "✅" if is_verified else "⚠️"
    status_text = "Verified" if is_verified else "Not Verified"
    remaining_downloads = max(0, FREE_DOWNLOAD_LIMIT - user_downloads)
    
    await query.edit_message_text(
        f"📊 **Your Status**\n\n"
        f"👤 **User ID:** `{user_id}`\n"
        f"{status_emoji} **Status:** {status_text}\n"
        f"📥 **Downloads Used:** {user_downloads}/{FREE_DOWNLOAD_LIMIT}\n"
        f"🆓 **Remaining Free:** {remaining_downloads}\n"
        f"⭐ **Account Type:** {'Premium' if is_verified else 'Free'}\n\n"
        f"📈 **Download History:**\n"
        f"• Today: {user_downloads} files\n"
        f"• This week: {user_downloads} files\n"
        f"• Total: {user_downloads} files\n\n"
        f"🎯 **Next Steps:**\n"
        f"{'🎉 Enjoy unlimited downloads!' if is_verified else '🔓 Complete verification for unlimited access'}",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_why_verify_callback(query, context):
    """Handle why verification callback"""
    keyboard = [
        [InlineKeyboardButton("🔓 Start Verification", callback_data="start_verification")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="verification_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "❓ **Why Verification is Required**\n\n"
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
        "🎯 **What You Get**\n"
        "• ♾️ Unlimited downloads\n"
        "• 🚀 Priority support\n"
        "• 📱 Mobile optimized\n"
        "• 🎥 Original video quality\n\n"
        "✅ **One-time verification - Use forever!**",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_start_verification_callback(query, context):
    """Handle start verification callback - ENHANCED VERSION"""
    user_id = query.from_user.id
    
    try:
        # Generate multiple verification options
        verification_links = [
            f"https://publicearn.com/verify?user={user_id}&ref=terabox&type=1",
            f"https://earnow.online/verify?user={user_id}&source=terabox",
            f"https://shortlink-generator.com/verify?uid={user_id}&bot=terabox"
        ]
        
        keyboard = [
            [InlineKeyboardButton("🔗 Verification Option 1", url=verification_links[0])],
            [InlineKeyboardButton("🔗 Verification Option 2", url=verification_links[1])],
            [InlineKeyboardButton("🔗 Verification Option 3", url=verification_links[2])],
            [InlineKeyboardButton("❓ Why Verification?", callback_data="why_verify")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="verification_menu")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"🔐 **Verification Links Generated**\n\n"
            f"**Choose any verification option below:**\n\n"
            f"**📋 Instructions:**\n"
            f"**Step 1:** Click any verification button\n"
            f"**Step 2:** Complete the quick task (30 seconds)\n"
            f"**Step 3:** Return and enjoy unlimited downloads!\n\n"
            f"**👤 User ID:** `{user_id}`\n"
            f"**⏱️ Status:** Pending verification\n"
            f"**🎯 Reward:** Unlimited downloads forever\n\n"
            f"**💡 Tips:**\n"
            f"• Use a different link if one doesn't work\n"
            f"• Complete verification within 10 minutes\n"
            f"• Return to the bot after completion\n\n"
            f"✅ **After verification: Download any Terabox file instantly!**",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
        LOGGER.info(f"✅ Verification links generated for user {user_id}")
        
    except Exception as e:
        LOGGER.error(f"❌ Verification callback error: {e}")
        
        keyboard = [
            [InlineKeyboardButton("🔄 Try Again", callback_data="start_verification")],
            [InlineKeyboardButton("🔙 Back", callback_data="verification_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"❌ **Verification Generation Error**\n\n"
            f"Unable to generate verification links right now.\n\n"
            f"**Please:**\n"
            f"• Try again in a few seconds\n"
            f"• Contact support if problem persists\n"
            f"• Use /start to refresh the bot\n\n"
            f"**Error Code:** `VER_001`\n"
            f"**User ID:** `{user_id}`",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

async def handle_verification_menu_callback(query, context):
    """Handle verification menu callback"""
    user_id = query.from_user.id
    
    keyboard = [
        [InlineKeyboardButton("🔓 Start Verification", callback_data="start_verification")],
        [InlineKeyboardButton("❓ Why Verification?", callback_data="why_verify")],
        [InlineKeyboardButton("📊 Check Status", callback_data="status")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="help")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🔐 **Verification Center**\n\n"
        f"**Current Status:** You've reached your download limit ({FREE_DOWNLOAD_LIMIT}/3 free downloads)\n\n"
        "**To continue downloading:**\n"
        "• Click 'Start Verification' below\n"
        "• Complete the quick verification process\n"
        "• Return and get unlimited downloads!\n\n"
        "**⏱️ Verification Process:**\n"
        "• Takes only 30-60 seconds\n"
        "• One-time process\n"
        "• Safe and secure\n"
        "• Works on mobile & desktop\n\n"
        "**🎁 Benefits After Verification:**\n"
        "• ♾️ Unlimited Terabox downloads\n"
        "• 🚀 Priority download speeds\n"
        "• 🎥 Original video quality\n"
        "• 📱 Mobile optimized experience",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

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
        f"• General questions: Support group\n\n"
        f"**🕒 Support Hours:**\n"
        f"24/7 community support available!",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_help_callback(query, context):
    """Handle help/main menu callback"""
    keyboard = [
        [InlineKeyboardButton("ℹ️ About Bot", callback_data="about")],
        [InlineKeyboardButton("📊 My Status", callback_data="status")],
        [InlineKeyboardButton("📞 Contact", callback_data="contact")],
        [InlineKeyboardButton("🔐 Verification", callback_data="verification_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"🎯 **{BOT_NAME} - Main Menu**\n\n"
        f"**🚀 Quick Start:**\n"
        f"• Send any Terabox link to download\n"
        f"• Get {FREE_DOWNLOAD_LIMIT} free downloads daily\n"
        f"• Verify for unlimited access\n\n"
        f"**📱 Supported Formats:**\n"
        f"• 🎥 Videos (MP4, AVI, MKV, MOV, etc.)\n"
        f"• 🖼️ Images (JPG, PNG, GIF, etc.)\n"
        f"• 📁 Documents (PDF, ZIP, etc.)\n\n"
        f"**✨ Features:**\n"
        f"• Original quality downloads\n"
        f"• Video thumbnails included\n"
        f"• Fast micro-chunk technology\n"
        f"• Mobile-friendly interface\n\n"
        f"**💡 Tips:**\n"
        f"• Send links directly (no commands needed)\n"
        f"• Verify once for unlimited downloads\n"
        f"• Join our channel for updates",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# ✅ Export the main handler function
def get_callback_handler():
    """Get the callback query handler"""
    return CallbackQueryHandler(handle_callback_queries)
    
