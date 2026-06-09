import subprocess
from pathlib import Path

class M3U8Downloader:
    def __init__(self, timeout=300):
        self.timeout = timeout
        self._check_ffmpeg()
    
    @staticmethod
    def _check_ffmpeg():
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        except:
            raise RuntimeError("FFmpeg not installed. Install from https://ffmpeg.org")
    
    def download(self, url, output_file, verbose=True):
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        cmd = ['ffmpeg', '-i', url, '-c', 'copy', '-y', output_file]
        
        try:
            subprocess.run(cmd, check=True, timeout=self.timeout)
            return True
        except Exception as e:
            raise RuntimeError(f"Download failed: {str(e)}")
