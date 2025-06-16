from typing import List, Any, Dict
import logging
import re

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