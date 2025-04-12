from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import subprocess
from dotenv import load_dotenv
import os
import re
import glob


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Halo! Kirim link Instagram ke sini, nanti aku kirim balik isinya.")


def is_instagram_url(url):
    return re.match(r'https?://(www\.)?instagram\.com/(p|reel|tv)/[\w\-]+',
                    url)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text.strip()
    if is_instagram_url(message):
        await update.message.reply_text("Tunggu sebentar, sedang didownload..."
                                        )

        try:
            output_template = "ig_content_%(autonumber)s.%(ext)s"
            cmd = ["yt-dlp", "-o", output_template, message]
            subprocess.run(cmd, check=True)

            files = sorted(glob.glob("ig_content_*"))
            if not files:
                await update.message.reply_text("Tidak ditemukan media.")
                return

            for file in files:
                if file.endswith(".mp4"):
                    await update.message.reply_video(video=open(file, 'rb'))
                else:
                    await update.message.reply_photo(photo=open(file, 'rb'))
                os.remove(file)
        except Exception as e:
            await update.message.reply_text(f"Error saat download: {e}")
    else:
        await update.message.reply_text(
            "Kirim link postingan Instagram yang valid.")


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()  # <-- WAJIB ditaruh sebelum os.getenv

    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        raise ValueError("BOT_TOKEN tidak ditemukan di .env")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot aktif...")
    app.run_polling()
