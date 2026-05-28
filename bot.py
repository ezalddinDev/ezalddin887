import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import instaloader

BOT_TOKEN = "5464450219:AAGoP5nI5sSu27CyMcKbGVvOaD-7z-1ROgU"

# إعداد instaloader
L = instaloader.Instaloader(
    download_videos=True,
    download_video_thumbnails=False,
    download_geotags=False,
    download_comments=False,
    save_metadata=False,
    quiet=True
)

# لو عندك حساب انستا (اختياري لكن يحسن الأداء)
# L.login("your_username", "your_password")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 هلا! أنا بوت تحميل من انستقرام\n\n"
        "📎 أرسل لي رابط البوست أو الريلز وبحمله لك!\n\n"
        "✅ يدعم:\n"
        "- 📹 ريلز\n"
        "- 🖼️ صور\n"
        "- 🎬 فيديوهات البوستات"
    )

def extract_shortcode(url: str):
    """استخرج الشورت كود من الرابط"""
    import re
    patterns = [
        r'instagram\.com/p/([A-Za-z0-9_-]+)',
        r'instagram\.com/reel/([A-Za-z0-9_-]+)',
        r'instagram\.com/reels/([A-Za-z0-9_-]+)',
        r'instagram\.com/tv/([A-Za-z0-9_-]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

async def download_instagram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    if "instagram.com" not in url:
        await update.message.reply_text("❌ أرسل رابط انستقرام صحيح!")
        return

    shortcode = extract_shortcode(url)
    if not shortcode:
        await update.message.reply_text("❌ ما قدرت أقرأ الرابط، تأكد منه!")
        return

    msg = await update.message.reply_text("⏳ جاري التحميل...")

    try:
        os.makedirs("downloads", exist_ok=True)

        # تحميل البوست
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        L.download_post(post, target="downloads")

        await msg.edit_text("✅ تم التحميل، جاري الإرسال...")

        # ابحث عن الملفات المحملة
        sent = False
        for file in os.listdir("downloads"):
            filepath = os.path.join("downloads", file)

            # إرسال فيديو
            if file.endswith(".mp4"):
                with open(filepath, 'rb') as f:
                    await update.message.reply_video(
                        video=f,
                        caption=f"🎬 {post.title or 'انستقرام'}",
                        read_timeout=60,
                        write_timeout=60
                    )
                sent = True

            # إرسال صورة
            elif file.endswith(".jpg") or file.endswith(".png"):
                with open(filepath, 'rb') as f:
                    await update.message.reply_photo(
                        photo=f,
                        caption=f"📸 {post.title or 'انستقرام'}"
                    )
                sent = True

            # حذف الملف
            os.remove(filepath)

        if not sent:
            await msg.edit_text("❌ ما لقيت ملفات للإرسال!")
        else:
            await msg.delete()

    except instaloader.exceptions.InstaloaderException as e:
        await msg.edit_text(f"❌ خطأ في انستقرام: {str(e)}")
    except Exception as e:
        await msg.edit_text(f"❌ صار خطأ: {str(e)}")

async def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_instagram))

    print("✅ البوت شغال...")
    await app.run_polling()

def main():
    app.run_polling()

if __name__ == "__main__":
    main()

