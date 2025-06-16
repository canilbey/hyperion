from typing import List, Any
import logging
import os
import re
import unicodedata
from unstructured.partition.auto import partition

class FileParsingService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def detect_file_type(self, file_path: str) -> str:
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        if ext == '.pdf':
            return 'pdf'
        elif ext == '.docx':
            return 'docx'
        elif ext in ['.html', '.htm']:
            return 'html'
        elif ext in ['.txt', '.md', '.rst']:
            return 'text'
        # Magic number kontrolü eklenebilir
        return 'unknown'

    def clean_text(self, text):
        if not isinstance(text, str):
            text = str(text)
        text = unicodedata.normalize('NFKC', text)
        text = ''.join(c for c in text if c.isprintable())
        text = re.sub(r'\s+', ' ', text)
        return text

    def safe_utf8(self, text):
        if not isinstance(text, str):
            text = str(text)
        return text.encode('utf-8', errors='replace').decode('utf-8', errors='replace')

    def parse(self, file_path: str) -> List[Any]:
        self.logger.info(f"Parsing file: {file_path}")
        try:
            elements = partition(
                filename=file_path,
                strategy="hi_res",
                infer_table_structure=True,
                extract_images_in_pdf=False,
                chunking_strategy="by_title",
                max_characters=4000,
                combine_text_under_n_chars=2000,
            )
            cleaned_elements = []
            for el in elements:
                if hasattr(el, 'text') and el.text and el.text.strip():
                    cleaned_text = self.safe_utf8(self.clean_text(el.text))
                    if cleaned_text.strip():
                        el.text = cleaned_text
                        cleaned_elements.append(el)
            self.logger.info(f"Successfully parsed {len(cleaned_elements)} elements from {os.path.basename(file_path)}")
            return cleaned_elements
        except Exception as e:
            self.logger.error(f"Unstructured parsing failed for {file_path}: {str(e)}")
            # Fallback: PyPDF2 for PDF
            if self.detect_file_type(file_path) == 'pdf':
                try:
                    import PyPDF2
                    content = ""
                    with open(file_path, 'rb') as f:
                        reader = PyPDF2.PdfReader(f)
                        for page in reader.pages:
                            content += page.extract_text() + "\n"
                    if content.strip():
                        content = self.safe_utf8(self.clean_text(content))
                        return [{'text': content, 'type': 'text'}]
                except Exception as pdf_error:
                    self.logger.error(f"PyPDF2 fallback failed: {str(pdf_error)}")
            # Fallback: text file
            try:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                content = self.safe_utf8(self.clean_text(content))
                return [{'text': content, 'type': 'text'}]
            except Exception as text_error:
                self.logger.error(f"Text fallback failed: {str(text_error)}")
            # Son çare: manuel binary
            try:
                with open(file_path, 'rb') as f:
                    raw_bytes = f.read()
                content = ''.join(chr(b) for b in raw_bytes if 32 <= b <= 126 or b in [9, 10, 13])
                content = self.safe_utf8(self.clean_text(content))
                if content.strip():
                    return [{'text': content, 'type': 'text'}]
            except Exception as manual_error:
                self.logger.error(f"Manual processing also failed: {str(manual_error)}")
            return [] 