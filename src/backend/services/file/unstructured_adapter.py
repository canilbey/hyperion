from unstructured.partition.text import partition_text
from unstructured.partition.html import partition_html
from unstructured.partition.auto import partition
import os
import logging
import re
import unicodedata


def clean_text(text):
    if not isinstance(text, str):
        text = str(text)
    text = unicodedata.normalize('NFKC', text)
    text = ''.join(c for c in text if c.isprintable())
    text = re.sub(r'\s+', ' ', text)
    return text

def safe_utf8(text):
    if not isinstance(text, str):
        text = str(text)
    return text.encode('utf-8', errors='replace').decode('utf-8', errors='replace')

def is_pdf_file(file_path: str) -> bool:
    """
    Dosyanın PDF olup olmadığını hem uzantıdan hem de magic number ile kontrol eder.
    """
    _, ext = os.path.splitext(file_path)
    if ext.lower() == '.pdf':
        return True
    try:
        with open(file_path, 'rb') as f:
            header = f.read(5)
            if header == b'%PDF-':
                return True
    except Exception:
        pass
    return False

# NLTK punkt_tab download - runtime'da, sadece ilk ihtiyaçta
_nltk_checked = False
def ensure_nltk_data():
    global _nltk_checked
    if _nltk_checked:
        return
    try:
        import nltk
        nltk.data.find('tokenizers/punkt_tab')
        _nltk_checked = True
    except LookupError:
        try:
            import nltk
            nltk.download('punkt_tab', quiet=True)
            logging.getLogger(__name__).info("NLTK punkt_tab downloaded successfully")
            _nltk_checked = True
        except Exception as e:
            logging.getLogger(__name__).warning(f"NLTK punkt_tab download failed: {e}")
            _nltk_checked = True

def get_optimal_strategy(file_path: str, file_size: int = None) -> str:
    """
    Dosya boyutu ve tipine göre en optimal unstructured strategy'yi belirler.
    
    Strategies:
    - 'fast': Hızlı parsing, düşük kalite (küçük dosyalar için)
    - 'hi_res': Yüksek kalite parsing, yavaş (büyük/karmaşık dosyalar için)  
    - 'auto': Otomatik seçim
    """
    if file_size is None:
        try:
            file_size = os.path.getsize(file_path)
        except:
            file_size = 0
    
    # 5MB altı dosyalar için fast strategy
    if file_size < 5 * 1024 * 1024:
        return 'fast'
    # 50MB üstü dosyalar için fast strategy (performans için)
    elif file_size > 50 * 1024 * 1024:
        return 'fast'
    # Orta boyut dosyalar için hi_res
    else:
        return 'hi_res'

def parse_document(file_path: str):
    """
    Belgeyi unstructured ile en yüksek kaliteyle (full) böl ve element listesini döndür.
    Her zaman partition fonksiyonu ve gelişmiş parametrelerle çalışır.
    """
    logger = logging.getLogger(__name__)
    ensure_nltk_data()
    try:
        file_size = os.path.getsize(file_path)
        logger.info(f"Parsing {os.path.basename(file_path)} (size: {file_size} bytes) with strategy: full")
        elements = partition(
            filename=file_path,
            strategy="hi_res",  # Her zaman en yüksek kalite
            infer_table_structure=True,  # Tablo yapısı çıkarımı aktif
            extract_images_in_pdf=True,  # Görsel çıkarımı aktif
            include_page_breaks=True,
            chunking_strategy="by_title",
            max_characters=4000,
            new_after_n_chars=3800,
            combine_text_under_n_chars=2000,
        )
        cleaned_elements = []
        for el in elements:
            if hasattr(el, 'text') and el.text and el.text.strip():
                cleaned_text = safe_utf8(clean_text(el.text))
                if cleaned_text.strip():
                    el.text = cleaned_text
                    cleaned_elements.append(el)
        logger.info(f"Successfully parsed {len(cleaned_elements)} elements from {os.path.basename(file_path)} using full strategy")
        return cleaned_elements
    except Exception as e:
        logger.error(f"Unstructured parsing failed for {file_path}: {str(e)}")
        raise 