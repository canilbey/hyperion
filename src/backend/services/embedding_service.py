from sentence_transformers import SentenceTransformer
from typing import List
import threading

class EmbeddingService:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model_name = model_name
        self._lock = threading.Lock()
        self.model = SentenceTransformer(model_name)

    def embed(self, texts: List[str]) -> List[List[float]]:
        with self._lock:
            return self.model.encode(texts, convert_to_numpy=False, show_progress_bar=False)

    def get_model_name(self) -> str:
        return self.model_name

    def available_models(self) -> List[str]:
        # Geliştirilebilir: Model havuzunu dinamik olarak döndürmek için
        return ['all-MiniLM-L6-v2', 'all-mpnet-base-v2', 'paraphrase-MiniLM-L6-v2'] 