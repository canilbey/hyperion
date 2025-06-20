from typing import List, Any, Dict
import logging
import re
import nltk
try:
    import tiktoken
    def count_tokens(text, model="gpt-3.5-turbo"):
        enc = tiktoken.encoding_for_model(model)
        return len(enc.encode(text))
except ImportError:
    def count_tokens(text, model=None):
        # Fallback: kelime sayısını 1.5 ile çarp
        return int(len(text.split()) * 1.5)

class ChunkingService:
    def __init__(self, chunk_size: int = 4000, chunk_overlap: int = 200):
        self.logger = logging.getLogger(__name__)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, elements: List[Any]) -> List[Dict]:
        """
        Başlık bazlı chunking (by_title) veya sabit boyutlu chunking.
        Her chunk'a metadata ekler: başlık, tip, sıra, offset, parent_id.
        """
        self.logger.info(f"Chunking {len(elements)} elements")
        chunks = []
        current_chunk = []
        current_title = None
        char_count = 0
        order = 0
        for el in elements:
            text = getattr(el, 'text', None) or el.get('text', None)
            if not text or not text.strip():
                continue
            # Başlık tespiti (örnek: Heading, Title, Section, vs.)
            title = getattr(el, 'metadata', {}).get('title') or getattr(el, 'category', None) or None
            if hasattr(el, 'category') and el.category and 'title' in el.category.lower():
                # Unstructured elementlerde başlık varsa
                if current_chunk:
                    chunks.append({
                        'content': '\n'.join(current_chunk),
                        'title': current_title or 'Untitled',
                        'order': order,
                        'metadata': {},
                    })
                    order += 1
                    current_chunk = []
                    char_count = 0
                current_title = text.strip()
                continue
            # Chunk boyutu kontrolü
            if char_count + len(text) > self.chunk_size:
                chunks.append({
                    'content': '\n'.join(current_chunk),
                    'title': current_title or 'Untitled',
                    'order': order,
                    'metadata': {},
                })
                order += 1
                # Overlap uygula
                if self.chunk_overlap > 0 and current_chunk:
                    overlap_text = ''.join(current_chunk)[-self.chunk_overlap:]
                    current_chunk = [overlap_text]
                    char_count = len(overlap_text)
                else:
                    current_chunk = []
                    char_count = 0
            current_chunk.append(text.strip())
            char_count += len(text)
        # Son chunk
        if current_chunk:
            chunks.append({
                'content': '\n'.join(current_chunk),
                'title': current_title or 'Untitled',
                'order': order,
                'metadata': {},
            })
        self.logger.info(f"Created {len(chunks)} chunks")
        return chunks

def paragraph_chunking(text: str, max_tokens: int = 500, overlap_sentences: int = 2, lang="turkish") -> list:
    """
    Paragraf bazlı chunking. Paragraflar 500 tokendan uzunsa, cümle bazında bölünür ve overlap uygulanır.
    """
    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    chunks = []
    chunk_id = 0
    for para_idx, para in enumerate(paragraphs):
        para_tokens = count_tokens(para)
        if para_tokens <= max_tokens:
            chunks.append({
                "content": para,
                "order": chunk_id,
                "metadata": {"paragraph_index": para_idx}
            })
            chunk_id += 1
        else:
            # Cümle bazında böl
            try:
                sentences = nltk.sent_tokenize(para, language=lang)
            except Exception:
                sentences = [para]
            current = []
            current_tokens = 0
            sent_idx = 0
            while sent_idx < len(sentences):
                sent = sentences[sent_idx]
                sent_tokens = count_tokens(sent)
                if current_tokens + sent_tokens > max_tokens and current:
                    # Overlap uygula
                    overlap = sentences[max(0, sent_idx-overlap_sentences):sent_idx]
                    chunk_text = ' '.join(current + overlap)
                    chunks.append({
                        "content": chunk_text,
                        "order": chunk_id,
                        "metadata": {"paragraph_index": para_idx, "overlap": overlap_sentences}
                    })
                    chunk_id += 1
                    # Overlap ile yeni chunk başlat
                    current = list(overlap)
                    current_tokens = sum(count_tokens(s) for s in current)
                current.append(sent)
                current_tokens += sent_tokens
                sent_idx += 1
            if current:
                chunk_text = ' '.join(current)
                chunks.append({
                    "content": chunk_text,
                    "order": chunk_id,
                    "metadata": {"paragraph_index": para_idx, "overlap": overlap_sentences}
                })
                chunk_id += 1
    return chunks 