from flask import Flask, request, jsonify
import os
from src.m3u8_downloader import M3U8Downloader
from src.pdf_extractor import PDFExtractor
from src.text_to_video import TextToVideo

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "service": "Text-to-Video Converter API",
        "status": "running",
        "version": "1.0.0"
    })

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/api/download-m3u8', methods=['POST'])
def download_m3u8():
    try:
        data = request.json
        url = data.get('url')
        downloader = M3U8Downloader()
        downloader.download(url, '/tmp/video.mp4')
        return jsonify({"status": "success", "message": "Downloaded"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/extract-pdf', methods=['POST'])
def extract_pdf():
    try:
        data = request.json
        pdf_path = data.get('pdf')
        extractor = PDFExtractor()
        content = extractor.extract(pdf_path)
        return jsonify({"status": "success", "content": content}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
