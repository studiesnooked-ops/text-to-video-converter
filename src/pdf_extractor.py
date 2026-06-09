import PyPDF2
import requests
from pathlib import Path

class PDFExtractor:
    def extract(self, file_path, include_metadata=True):
        if file_path.startswith('http'):
            file_path = self._download_pdf(file_path)
        
        try:
            with open(file_path, 'rb') as file:
                pdf = PyPDF2.PdfReader(file)
                text_content = []
                
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text.strip():
                        text_content.append(f"\n--- Page {page_num} ---\n")
                        text_content.append(text)
                
                return ''.join(text_content)
        except Exception as e:
            raise RuntimeError(f"Failed to extract PDF: {str(e)}")
    
    @staticmethod
    def _download_pdf(url, timeout=30):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            temp_path = Path('temp_pdf.pdf')
            temp_path.write_bytes(response.content)
            return str(temp_path)
        except Exception as e:
            raise RuntimeError(f"Failed to download PDF: {str(e)}")
