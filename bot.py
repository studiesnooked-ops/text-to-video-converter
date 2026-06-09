#!/usr/bin/env python3
"""
Telegram Bot for Text-to-Video Converter
Handles: M3U8 downloads, PDF extraction, Text-to-video conversion
"""

import os
import logging
from dotenv import load_dotenv
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes
from pathlib import Path
import sys

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

# Create output directory
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)


class TextToVideoBot:
    """Telegram Bot for Text-to-Video Conversion"""
    
    def __init__(self):
        self.downloader = M3U8Downloader()
        self.extractor = PDFExtractor()
        self.converter = TextToVideo()
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        welcome_text = f"""
🎬 Welcome to Text-to-Video Converter Bot! 🎬

Hi {user.mention_html()}! 

I can help you:
✅ Download videos from M3U8 playlists
✅ Extract text from PDF files
✅ Convert text to video
✅ Run complete pipelines

Use /help to see all commands.
        """
        await update.message.reply_html(welcome_text)
        logger.info(f"User {user.id} started the bot")
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
📖 Available Commands:

🎥 *Video Operations*
/download_m3u8 - Download video from M3U8 URL
/convert_text - Convert text to video

📄 *PDF Operations*
/extract_pdf - Extract text from PDF file

🔄 *Pipeline*
/pipeline - Run complete pipeline

ℹ️ *Information*
/status - Check bot status
/help - Show this message

💡 *Usage Examples:*

1️⃣ Download M3U8:
/download_m3u8 https://example.com/playlist.m3u8

2️⃣ Extract PDF:
/extract_pdf https://example.com/document.pdf

3️⃣ Convert Text to Video:
/convert_text Your text here

4️⃣ Full Pipeline:
/pipeline https://example.com/playlist.m3u8 https://example.com/doc.pdf
        """
        await update.message.reply_markdown(help_text)
    
    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        try:
            status_text = f"""
✅ Bot Status: ONLINE

📊 System Information:
• Bot: Text-to-Video Converter
• Version: 1.0.0
• Status: Running
• Output Directory: {OUTPUT_DIR}

🔧 Available Tools:
• M3U8 Downloader: ✅ Active
• PDF Extractor: ✅ Active
• Text-to-Video: ✅ Active

All systems operational! 🚀
            """
            await update.message.reply_markdown(status_text)
        except Exception as e:
            await update.message.reply_text(f"❌ Error checking status: {str(e)}")
    
    async def download_m3u8(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /download_m3u8 command"""
        try:
            if not context.args:
                await update.message.reply_text(
                    "❌ Please provide M3U8 URL\n\n"
                    "Usage: /download_m3u8 https://example.com/playlist.m3u8"
                )
                return
            
            url = context.args[0]
            await update.message.reply_text("📥 Downloading M3U8 video...\nThis may take a while...")
            
            output_file = os.path.join(OUTPUT_DIR, 'downloaded_video.mp4')
            self.downloader.download(url, output_file, verbose=False)
            
            with open(output_file, 'rb') as video:
                await update.message.reply_document(
                    document=video,
                    caption="✅ Video downloaded successfully!"
                )
            logger.info(f"Downloaded M3U8 video for user {update.effective_user.id}")
        
        except Exception as e:
            error_msg = f"❌ Download failed: {str(e)}"
            await update.message.reply_text(error_msg)
            logger.error(f"Error downloading M3U8: {str(e)}")
    
    async def extract_pdf(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /extract_pdf command"""
        try:
            if not context.args:
                await update.message.reply_text(
                    "❌ Please provide PDF URL or file path\n\n"
                    "Usage: /extract_pdf https://example.com/document.pdf"
                )
                return
            
            pdf_path = context.args[0]
            await update.message.reply_text("📄 Extracting PDF content...\nPlease wait...")
            
            content = self.extractor.extract(pdf_path)
            
            # Save to file if content is large
            if len(content) > 4096:
                output_file = os.path.join(OUTPUT_DIR, 'extracted_text.txt')
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                with open(output_file, 'rb') as doc:
                    await update.message.reply_document(
                        document=doc,
                        caption=f"✅ PDF extracted! Total characters: {len(content)}"
                    )
            else:
                await update.message.reply_text(f"✅ Extracted Content:\n\n{content}")
            
            logger.info(f"Extracted PDF for user {update.effective_user.id}")
        
        except Exception as e:
            error_msg = f"❌ PDF extraction failed: {str(e)}"
            await update.message.reply_text(error_msg)
            logger.error(f"Error extracting PDF: {str(e)}")
    
    async def convert_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /convert_text command"""
        try:
            if not context.args:
                await update.message.reply_text(
                    "❌ Please provide text\n\n"
                    'Usage: /convert_text Your text here'
                )
                return
            
            text = ' '.join(context.args)
            await update.message.reply_text("🎬 Converting text to video...\nThis may take a while...")
            
            # Save text to temporary file
            temp_text_file = os.path.join(OUTPUT_DIR, 'temp_input.txt')
            with open(temp_text_file, 'w', encoding='utf-8') as f:
                f.write(text)
            
            output_file = os.path.join(OUTPUT_DIR, 'text_video.mp4')
            self.converter.convert(temp_text_file, output_file)
            
            with open(output_file, 'rb') as video:
                await update.message.reply_document(
                    document=video,
                    caption="✅ Video created successfully!"
                )
            logger.info(f"Created text video for user {update.effective_user.id}")
        
        except Exception as e:
            error_msg = f"❌ Text conversion failed: {str(e)}"
            await update.message.reply_text(error_msg)
            logger.error(f"Error converting text: {str(e)}")
    
    async def pipeline(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /pipeline command - run complete workflow"""
        try:
            if len(context.args) < 2:
                await update.message.reply_text(
                    "❌ Please provide M3U8 URL and PDF URL\n\n"
                    "Usage: /pipeline https://example.com/playlist.m3u8 https://example.com/doc.pdf"
                )
                return
            
            m3u8_url = context.args[0]
            pdf_url = context.args[1]
            
            await update.message.reply_text("🔄 Running complete pipeline...\nProcessing M3U8, PDF, and creating video...")
            
            # Step 1: Download M3U8
            await update.message.reply_text("📹 Step 1: Downloading M3U8 video...")
            video_file = os.path.join(OUTPUT_DIR, 'pipeline_video.mp4')
            self.downloader.download(m3u8_url, video_file, verbose=False)
            await update.message.reply_text("✅ Video downloaded")
            
            # Step 2: Extract PDF
            await update.message.reply_text("📄 Step 2: Extracting PDF...")
            pdf_content = self.extractor.extract(pdf_url)
            pdf_output = os.path.join(OUTPUT_DIR, 'pipeline_notes.txt')
            with open(pdf_output, 'w', encoding='utf-8') as f:
                f.write(pdf_content)
            await update.message.reply_text("✅ PDF extracted")
            
            # Step 3: Create video
            await update.message.reply_text("🎬 Step 3: Creating text video...")
            text_video_output = os.path.join(OUTPUT_DIR, 'pipeline_text_video.mp4')
            self.converter.convert(pdf_output, text_video_output)
            await update.message.reply_text("✅ Text video created")
            
            # Send results
            await update.message.reply_text("📦 Pipeline completed! Sending files...")
            
            with open(video_file, 'rb') as video:
                await update.message.reply_document(
                    document=video,
                    caption="📹 Downloaded Video"
                )
            with open(pdf_output, 'rb') as doc:
                await update.message.reply_document(
                    document=doc,
                    caption="📄 Extracted PDF Text"
                )
            with open(text_video_output, 'rb') as video:
                await update.message.reply_document(
                    document=video,
                    caption="🎬 Generated Text Video"
                )
            
            logger.info(f"Pipeline completed for user {update.effective_user.id}")
        
        except Exception as e:
            error_msg = f"❌ Pipeline failed: {str(e)}"
            await update.message.reply_text(error_msg)
            logger.error(f"Error in pipeline: {str(e)}")
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")
        if update and update.message:
            try:
                await update.message.reply_text(f"❌ An error occurred: {str(context.error)}")
            except Exception as e:
                logger.error(f"Error in error handler: {str(e)}")


def main() -> None:
    """Start the bot - use synchronous main for Render"""
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set in environment variables!")
        sys.exit(1)
    
    # Create bot application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Initialize bot handler
    bot = TextToVideoBot()
    
    # Register command handlers
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CommandHandler("help", bot.help))
    application.add_handler(CommandHandler("status", bot.status))
    application.add_handler(CommandHandler("download_m3u8", bot.download_m3u8))
    application.add_handler(CommandHandler("extract_pdf", bot.extract_pdf))
    application.add_handler(CommandHandler("convert_text", bot.convert_text))
    application.add_handler(CommandHandler("pipeline", bot.pipeline))
    
    # Error handler
    application.add_error_handler(bot.error_handler)
    
    # Set bot commands (this will run async internally)
    logger.info("Text-to-Video Telegram Bot starting...")
    
    try:
        # Run the bot - this blocks and runs the event loop
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)


# -----------------------------
# Flask web server for Render
# -----------------------------
from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route("/")
def home():
    return "Text-to-Video Bot is running!", 200

@app.route("/health")
def health():
    return {"status": "ok"}, 200

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
        use_reloader=False
    )

if __name__ == "__main__":
    # Start Flask server in background
    Thread(target=run_web, daemon=True).start()

    # Start Telegram bot
    main()
if __name__ == '__main__':
    main()
