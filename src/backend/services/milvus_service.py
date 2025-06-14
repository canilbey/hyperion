from pymilvus import Collection, CollectionSchema, FieldSchema, DataType, connections, utility
from typing import List, Optional
import numpy as np
import os
import json
import logging

class MilvusService:
    def __init__(self, host: str = None, port: str = None, collection_name: str = 'embeddings'):
        self.host = host or os.getenv('MILVUS_HOST', 'milvus')
        self.port = port or os.getenv('MILVUS_PORT', '19530')
        self.collection_name = collection_name
        self._connected = False
        self._collection = None
        self.logger = logging.getLogger(__name__)

    def _connect_and_init(self):
        if not self._connected:
            connections.connect(host=self.host, port=self.port)
            self._connected = True
        if self._collection is None:
            self._collection = self._get_or_create_collection(self.collection_name)

    def _get_or_create_collection(self, name: str) -> Collection:
        if utility.has_collection(name):
            return Collection(name)
        # Varsayılan şema: id (int64), embedding (float_vector), metadata (string)
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=384),  # MiniLM-L6-v2 için 384
            FieldSchema(name="metadata", dtype=DataType.VARCHAR, max_length=512)
        ]
        schema = CollectionSchema(fields, description="Embeddings collection")
        collection = Collection(name, schema)
        # Index oluştur
        index_params = {"index_type": "IVF_FLAT", "metric_type": "L2", "params": {"nlist": 128}}
        collection.create_index(field_name="embedding", index_params=index_params)
        collection.load()
        return collection

    def insert_embedding(self, embedding: List[float], metadata: str):
        self._connect_and_init()
        # Milvus float_vector field requires numpy array
        import numpy as np
        
        # Convert to numpy array regardless of input type
        if hasattr(embedding, 'tolist'):
            # If it's a tensor, convert to list first, then numpy
            embedding_list = embedding.tolist()
        else:
            embedding_list = list(embedding)
            
        # Create numpy array with explicit float32 dtype
        embedding_array = np.array(embedding_list, dtype=np.float32)
        
        # Metadata dict ise JSON'a çevir
        if isinstance(metadata, dict):
            metadata = json.dumps(metadata, ensure_ascii=False)
        
        # Milvus insert format: [values] not {"field": [values]}
        data = [
            [embedding_array],  # embedding field
            [metadata]          # metadata field
        ]
        self._collection.insert(data)

    def search(self, query_embedding: List[float], top_k: int = 5, filter_expr: Optional[str] = None, similarity_threshold: float = 0.5):
        self._connect_and_init()
        
        # Convert query embedding to proper format (same as insert_embedding)
        if hasattr(query_embedding, 'tolist'):
            # If it's a tensor, convert to list first, then numpy
            embedding_list = query_embedding.tolist()
        else:
            embedding_list = list(query_embedding)
            
        # Create numpy array with explicit float32 dtype
        embedding_array = np.array(embedding_list, dtype=np.float32)
        
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
        results = self._collection.search(
            data=[embedding_array],  # Use converted numpy array
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            expr=filter_expr,
            output_fields=["metadata"]  # Metadata field'ını da döndür
        )
        # L2 mesafesini benzerliğe çevir (örnek: similarity = 1 / (1 + distance))
        filtered_results = []
        for hit in results[0]:
            distance = getattr(hit, 'distance', None)
            similarity = 1 / (1 + distance) if distance is not None else 0
            self.logger.info(f"Milvus search result: distance={distance}, similarity={similarity}")
            if similarity >= similarity_threshold:
                filtered_results.append(hit)
        return [filtered_results] 