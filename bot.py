from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler

BOT_TOKEN = "PUT_YOUR_TOKEN"

GAME_URL = "https://username.github.io/repo-name/"

async def start(update, context):
    keyboard = [
        [InlineKeyboardButton("🚗 Play Car Game", web_app=WebAppInfo(url=GAME_URL))]
    ]

    await update.message.reply_text(
        "🎮 اضغط لتلعب",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))

app.run_polling()
