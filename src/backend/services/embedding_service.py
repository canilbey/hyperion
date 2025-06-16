from sentence_transformers import SentenceTransformer
from typing import List
import threading
import unicodedata
import re

class EmbeddingService:
    def __init__(self, model_name: str = 'paraphrase-multilingual-MiniLM-L12-v2'):
        self.model_name = model_name
        self._lock = threading.Lock()
        self.model = SentenceTransformer(model_name)

    def preprocess(self, text: str) -> str:
        # Unicode normalization, lower, strip, fazla boşluk temizliği
        text = unicodedata.normalize('NFC', text)
        text = text.lower().strip()
        text = re.sub(r'\s+', ' ', text)
        return text

    def embed(self, texts: List[str]) -> List[List[float]]:
        with self._lock:
            preprocessed = [self.preprocess(t) for t in texts]
            return self.model.encode(preprocessed, convert_to_numpy=False, show_progress_bar=False)

    def get_model_name(self) -> str:
        return self.model_name

    def available_models(self) -> List[str]:
        # Geliştirilebilir: Model havuzunu dinamik olarak döndürmek için
        return [
            'paraphrase-multilingual-MiniLM-L12-v2',
            'all-MiniLM-L6-v2',
            'all-mpnet-base-v2',
            'paraphrase-MiniLM-L6-v2'
        ]

    def embed_and_store_child_chunks(self, child_chunks: List[dict], milvus_service, parent_id: int):
        """
        Her bir child chunk'ın embedding'ini alır ve parent_id, type, order, metadata ile birlikte Milvus'a ekler.
        """
        texts = [chunk['content'] for chunk in child_chunks]
        embeddings = self.embed(texts)
        for chunk, embedding in zip(child_chunks, embeddings):
            metadata = {
                'parent_id': parent_id,
                'type': chunk.get('type'),
                'order': chunk.get('order'),
                'metadata': chunk.get('metadata')
            }
            milvus_service.insert_embedding(embedding, metadata) 