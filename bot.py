import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===== Configuration =====
# Telegram Bot Token
TELEGRAM_TOKEN = "7050427309:AAF7jc6SqN5SPgcbKL7i5lL9uxWFrxmpCOU"

# Replace these with your actual social media links
CHANNEL_USERNAME = "@your_channel"  # Example: "@crypto_news"
GROUP_USERNAME = "@your_group"     # Example: "@crypto_community"
TWITTER_URL = "https://twitter.com/your_twitter"  # Example: "https://twitter.com/elonmusk"
# =========================

# Conversation states
START_ROUTES, SUBMIT_WALLET = range(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send welcome message with join instructions"""
    user = update.effective_user
    
    # Create join buttons
    keyboard = [
        [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
        [InlineKeyboardButton("👥 Join Group", url=f"https://t.me/{GROUP_USERNAME[1:]}")],
        [InlineKeyboardButton("🐦 Follow Twitter", url=TWITTER_URL)],
        [InlineKeyboardButton("✅ I've Joined", callback_data='joined')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send welcome message with buttons
    await update.message.reply_text(
        f"👋 Welcome {user.mention_html()} to our SOL Airdrop Bot!\n\n"
        "📌 To participate in the airdrop:\n"
        f"1. Join our channel: {CHANNEL_USERNAME}\n"
        f"2. Join our group: {GROUP_USERNAME}\n"
        f"3. Follow our Twitter: {TWITTER_URL}\n\n"
        "Click ✅ after completing all steps",
        reply_markup=reply_markup,
        parse_mode="HTML"
    )
    return START_ROUTES

async def handle_join_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Prompt for wallet address after user confirms joining"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "✅ Participation confirmed!\n\n"
        "📥 Please send your SOL wallet address now:"
    )
    return SUBMIT_WALLET

async def handle_wallet_submission(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process submitted wallet address"""
    wallet_address = update.message.text
    user = update.effective_user
    
    # Send congratulations message
    await update.message.reply_text(
        f"🎉 Congratulations {user.mention_html()}!\n"
        "10 SOL is on its way to your wallet:\n"
        f"<code>{wallet_address}</code>\n\n"
        "⏳ Transaction will be completed within 24 hours\n"
        "⚠️ Note: This is a simulated airdrop. No actual tokens will be sent.",
        parse_mode="HTML"
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """End conversation"""
    await update.message.reply_text("Operation cancelled. Type /start to begin again.")
    return ConversationHandler.END

def main() -> None:
    """Run the bot"""
    # Create Telegram application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Conversation handler for the airdrop flow
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            START_ROUTES: [
                CallbackQueryHandler(handle_join_confirmation, pattern='^joined$')
            ],
            SUBMIT_WALLET: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_wallet_submission)
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    application.add_handler(conv_handler)
    
    # Check if running on Render
    if 'RENDER' in os.environ:
        # Production deployment (Render)
        port = int(os.environ.get('PORT', 10000))
        webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{TELEGRAM_TOKEN}"
        
        # Set up webhook
        application.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=TELEGRAM_TOKEN,
            webhook_url=webhook_url,
            drop_pending_updates=True
        )
        logger.info("Bot running in webhook mode on Render")
    else:
        # Local development
        application.run_polling(drop_pending_updates=True)
        logger.info("Bot running in polling mode locally")

if __name__ == '__main__':
    main()
