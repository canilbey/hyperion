from typing import List, Any, Dict
import logging
from sentence_transformers import SentenceTransformer

class EmbeddingService:
    def __init__(self, model_name: str = 'paraphrase-multilingual-MiniLM-L12-v2'):
        self.logger = logging.getLogger(__name__)
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name

    def embed(self, chunks: List[Dict]) -> List[Dict]:
        """
        Her chunk için embedding üretir ve metadata ile birlikte döner.
        """
        self.logger.info(f"Embedding {len(chunks)} chunks with model {self.model_name}")
        texts = [chunk['content'] for chunk in chunks]
        embeddings = self.model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
        results = []
        for chunk, embedding in zip(chunks, embeddings):
            results.append({
                'embedding': embedding,
                'content': chunk['content'],
                'title': chunk.get('title', 'Untitled'),
                'order': chunk.get('order', 0),
                'metadata': chunk.get('metadata', {}),
            })
        self.logger.info(f"Generated {len(results)} embeddings")
        return results 