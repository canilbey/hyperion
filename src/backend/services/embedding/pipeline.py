from sentence_transformers import SentenceTransformer
import unicodedata
import re
import logging

def clean_text_for_embedding(text):
    """
    Text'i embedding için güvenli hale getirir.
    Binary karakterleri ve encoding sorunlarını çözer.
    """
    if not isinstance(text, str):
        text = str(text)
    
    # Unicode normalization
    try:
        text = unicodedata.normalize('NFKC', text)
    except:
        pass
    
    # Sadece printable ASCII + temel Unicode karakterleri tut
    text = ''.join(char for char in text if ord(char) < 127 or char.isalnum() or char.isspace())
    
    # Fazla boşlukları temizle
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Çok kısa veya boş text'leri düzelt
    if len(text.strip()) < 3:
        text = "No readable content available"
    
    return text

def embed_chunks(chunks, model_name="paraphrase-multilingual-MiniLM-L12-v2"):
    """
    Verilen chunk listesini embedding modeline gönder ve vektörleri döndür.
    Text encoding sorunlarını çözer.
    """
    logger = logging.getLogger(__name__)
    
    try:
        model = SentenceTransformer(model_name)
        
        # Tüm chunk content'lerini güvenli hale getir
        texts = []
        for chunk in chunks:
            content = chunk.get("content", "")
            clean_content = clean_text_for_embedding(content)
            texts.append(clean_content)
        
        logger.info(f"Embedding {len(texts)} chunks with model {model_name}")
        
        # Embedding işlemi
        embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        
        logger.info(f"Successfully generated {len(embeddings)} embeddings")
        return embeddings
        
    except Exception as e:
        logger.error(f"Embedding failed: {str(e)}")
        # Fallback: boş embedding listesi döndür
        logger.warning("Returning empty embeddings as fallback")
        import numpy as np
        return np.array([[0.0] * 384 for _ in chunks])  # 384-dim default embedding size 