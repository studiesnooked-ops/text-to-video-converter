#!/usr/bin/env python3
"""
Telegram Bot for Text-to-Video Converter
Handles: M3U8 downloads, PDF extraction, Text-to-video conversion + Render Web Service support
"""

import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from pathlib import Path
import sys
from threading import Thread
from flask import Flask

from src.m3u8_downloader import M3U8Downloader
from src.pdf_extractor import PDFExtractor
from src.text_to_video import TextToVideo

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_CHAT_ID = int(os.getenv('TELEGRAM_CHAT_ID', '0'))
OUTPUT_DIR = os.getenv('OUTPUT_DIR', '/tmp/output')

Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)


# -----------------------------
# Flask Web Server (Render fix)
# -----------------------------
app = Flask(__name__)

@app.route("/")
def home():
    return "Text-to-Video Bot is running!", 200

@app.route("/health")
def health():
    return {"status": "ok"}, 200

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)


class TextToVideoBot:
    def __init__(self):
        self.downloader = M3U8Downloader()
        self.extractor = PDFExtractor()
        self.converter = TextToVideo()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        await update.message.reply_html(
            f"🎬 Welcome {user.mention_html()}!\n\n"
            "I can convert text, PDFs, and M3U8 videos into video format."
        )

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "/start - Start bot\n"
            "/download_m3u8 URL\n"
            "/extract_pdf URL\n"
            "/convert_text TEXT\n"
            "/pipeline URL URL"
        )

    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("✅ Bot is running fine.")

    async def download_m3u8(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            return await update.message.reply_text("Send: /download_m3u8 URL")

        url = context.args[0]
        file_path = os.path.join(OUTPUT_DIR, "video.mp4")

        await update.message.reply_text("📥 Downloading...")

        self.downloader.download(url, file_path, verbose=False)

        with open(file_path, "rb") as f:
            await update.message.reply_document(f)

    async def extract_pdf(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            return await update.message.reply_text("Send: /extract_pdf URL")

        pdf_url = context.args[0]

        await update.message.reply_text("📄 Extracting...")

        text = self.extractor.extract(pdf_url)

        output = os.path.join(OUTPUT_DIR, "pdf.txt")
        with open(output, "w", encoding="utf-8") as f:
            f.write(text)

        await update.message.reply_document(open(output, "rb"))

    async def convert_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            return await update.message.reply_text("Send: /convert_text YOUR TEXT")

        text = " ".join(context.args)

        input_file = os.path.join(OUTPUT_DIR, "input.txt")
        output_file = os.path.join(OUTPUT_DIR, "output.mp4")

        with open(input_file, "w", encoding="utf-8") as f:
            f.write(text)

        await update.message.reply_text("🎬 Creating video...")

        self.converter.convert(input_file, output_file)

        await update.message.reply_document(open(output_file, "rb"))

    async def pipeline(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if len(context.args) < 2:
            return await update.message.reply_text("Send: /pipeline M3U8_URL PDF_URL")

        m3u8_url = context.args[0]
        pdf_url = context.args[1]

        await update.message.reply_text("🚀 Running pipeline...")

        video_file = os.path.join(OUTPUT_DIR, "pipe_video.mp4")
        pdf_file = os.path.join(OUTPUT_DIR, "pipe_pdf.txt")
        final_video = os.path.join(OUTPUT_DIR, "pipe_output.mp4")

        self.downloader.download(m3u8_url, video_file, verbose=False)

        text = self.extractor.extract(pdf_url)
        with open(pdf_file, "w", encoding="utf-8") as f:
            f.write(text)

        self.converter.convert(pdf_file, final_video)

        await update.message.reply_document(open(video_file, "rb"))
        await update.message.reply_document(open(pdf_file, "rb"))
        await update.message.reply_document(open(final_video, "rb"))

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.error(f"Error: {context.error}")
        if update and update.message:
            await update.message.reply_text("❌ Error occurred")


def main():
    if not BOT_TOKEN:
        logger.error("BOT TOKEN missing!")
        sys.exit(1)

    application = Application.builder().token(BOT_TOKEN).build()

    bot = TextToVideoBot()

    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CommandHandler("help", bot.help))
    application.add_handler(CommandHandler("status", bot.status))
    application.add_handler(CommandHandler("download_m3u8", bot.download_m3u8))
    application.add_handler(CommandHandler("extract_pdf", bot.extract_pdf))
    application.add_handler(CommandHandler("convert_text", bot.convert_text))
    application.add_handler(CommandHandler("pipeline", bot.pipeline))

    application.add_error_handler(bot.error_handler)

    logger.info("Bot starting...")

    application.run_polling(allowed_updates=Update.ALL_TYPES)


# -----------------------------
# SINGLE ENTRY POINT (FIXED)
# -----------------------------
if __name__ == "__main__":
    Thread(target=run_web, daemon=True).start()
    main()
