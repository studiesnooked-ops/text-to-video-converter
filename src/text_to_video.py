from moviepy.editor import TextClip, CompositeVideoClip, ColorClip
from pathlib import Path

class TextToVideo:
    def __init__(self, default_fps=24):
        self.default_fps = default_fps
    
    def convert(self, text_file, output_file, settings=None):
        settings = settings or {}
        fontsize = settings.get('fontsize', 24)
        color = settings.get('color', 'white')
        duration_per_line = settings.get('duration_per_line', 2)
        width = settings.get('width', 1280)
        height = settings.get('height', 720)
        
        try:
            with open(text_file, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]
            
            if not lines:
                raise ValueError("Text file is empty")
            
            clips = []
            for i, line in enumerate(lines):
                txt_clip = TextClip(line, fontsize=fontsize, color=color, method='caption', size=(width-100, None))
                txt_clip = txt_clip.set_duration(duration_per_line).set_position('center').set_start(i * duration_per_line)
                clips.append(txt_clip)
            
            duration = len(lines) * duration_per_line
            bg_clip = ColorClip(size=(width, height), color=(0, 0, 0)).set_duration(duration)
            video = CompositeVideoClip([bg_clip] + clips, size=(width, height))
            
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            video.write_videofile(output_file, fps=24, verbose=False, logger=None)
            return True
        except Exception as e:
            raise RuntimeError(f"Conversion failed: {str(e)}")
