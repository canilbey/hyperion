import re
from typing import List, Dict, Optional
from backend.models import ParentChunk, ChildChunk

class Chunker:
    def __init__(self):
        pass

    def split_to_parent_chunks(self, text: str) -> List[Dict]:
        """
        Metni başlık/bölüm bazlı parent chunk'lara ayırır.
        Şimdilik örnek olarak Markdown H1/H2 başlıklarını kullanır.
        """
        parent_chunks = []
        current_title = None
        current_content = []
        order = 0
        for line in text.splitlines():
            if re.match(r'^(#|##) ', line):
                if current_content:
                    parent_chunks.append({
                        'title': current_title,
                        'content': '\n'.join(current_content),
                        'order': order
                    })
                    order += 1
                    current_content = []
                current_title = line.strip('# ').strip()
            else:
                current_content.append(line)
        if current_content:
            parent_chunks.append({
                'title': current_title,
                'content': '\n'.join(current_content),
                'order': order
            })
        return parent_chunks

    def split_to_child_chunks(self, parent_chunk: Dict) -> List[Dict]:
        """
        Parent chunk'ı semantic olarak child chunk'lara böler.
        Paragraf, kod bloğu, tablo gibi yapıları tespit eder.
        """
        content = parent_chunk['content']
        lines = content.split('\n')
        child_chunks = []
        buffer = []
        chunk_type = 'paragraph'
        order = 0
        for line in lines:
            if re.match(r'^```', line):
                if buffer:
                    child_chunks.append({
                        'content': '\n'.join(buffer),
                        'type': chunk_type,
                        'order': order
                    })
                    order += 1
                    buffer = []
                chunk_type = 'code' if chunk_type != 'code' else 'paragraph'
            elif re.match(r'^\|', line):
                if buffer and chunk_type != 'table':
                    child_chunks.append({
                        'content': '\n'.join(buffer),
                        'type': chunk_type,
                        'order': order
                    })
                    order += 1
                    buffer = []
                chunk_type = 'table'
                buffer.append(line)
            elif line.strip() == '':
                if buffer:
                    child_chunks.append({
                        'content': '\n'.join(buffer),
                        'type': chunk_type,
                        'order': order
                    })
                    order += 1
                    buffer = []
                chunk_type = 'paragraph'
            else:
                buffer.append(line)
        if buffer:
            child_chunks.append({
                'content': '\n'.join(buffer),
                'type': chunk_type,
                'order': order
            })
        return child_chunks 