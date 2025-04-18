from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from instaloader import Instaloader, Post
import os
import re
from dotenv import load_dotenv

load_dotenv()

INSTAGRAM_USERNAME = os.getenv("IG_USERNAME")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Init instaloader
loader = Instaloader()
loader.load_session_from_file(INSTAGRAM_USERNAME, f"session-{INSTAGRAM_USERNAME}")

def extract_shortcode(url):
    match = re.search(r'/p/([^/?]+)|/reel/([^/?]+)|/tv/([^/?]+)', url)
    return next((group for group in match.groups() if group), None)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Kirim link postingan Instagram, nanti aku kirim balik medianya!")

async def handle_instagram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    shortcode = extract_shortcode(url)
    if not shortcode:
        await update.message.reply_text("Link tidak valid.")
        return

    try:
        post = Post.from_shortcode(loader.context, shortcode)
        await update.message.reply_text("Mendapatkan media...")

        if post.typename == "GraphSidecar":  # carousel
            for node in post.get_sidecar_nodes():
                if node.is_video:
                    await update.message.reply_video(video=node.video_url)
                else:
                    await update.message.reply_photo(photo=node.display_url)
        else:
            if post.is_video:
                await update.message.reply_video(video=post.video_url)
            else:
                await update.message.reply_photo(photo=post.url)

    except Exception as e:
        await update.message.reply_text(f"Gagal download: {e}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_instagram))

    print("Bot aktif menggunakan Instaloader...")
    app.run_polling()
