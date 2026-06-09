import os
from dotenv import load_dotenv

load_dotenv()

OUTPUT_DIR = os.getenv('OUTPUT_DIR', 'output')
VIDEO_FPS = int(os.getenv('VIDEO_FPS', 24))
FONT_SIZE = int(os.getenv('FONT_SIZE', 24))
FONT_COLOR = os.getenv('FONT_COLOR', 'white')
BACKGROUND_COLOR = os.getenv('BACKGROUND_COLOR', 'black')
DURATION_PER_LINE = int(os.getenv('DURATION_PER_LINE', 2))
VIDEO_WIDTH = int(os.getenv('VIDEO_WIDTH', 1280))
VIDEO_HEIGHT = int(os.getenv('VIDEO_HEIGHT', 720))

os.makedirs(OUTPUT_DIR, exist_ok=True)
