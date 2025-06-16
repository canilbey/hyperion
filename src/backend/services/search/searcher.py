from typing import List, Any, Dict
import logging
from pymilvus import Collection, connections, CollectionSchema, FieldSchema, DataType, utility
import numpy as np
import os
import socket

class SearchService:
    def __init__(self, milvus_collection_name: str = 'rag_chunks'):
        self.logger = logging.getLogger(__name__)
        self.collection_name = milvus_collection_name
        # Bağlantı önceliği: ortam değişkeni > localhost > cihaz IP'si
        host = os.getenv('MILVUS_HOST')
        port = os.getenv('MILVUS_PORT', '19530')
        if not host:
            # Önce localhost'u dene
            try:
                import socket
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1)
                if s.connect_ex(('localhost', int(port))) == 0:
                    host = 'localhost'
                else:
                    # Son çare: cihazın local IP'sini bul
                    hostname = socket.gethostname()
                    local_ip = socket.gethostbyname(hostname)
                    host = local_ip
                s.close()
            except Exception as e:
                self.logger.warning(f"Milvus host tespiti başarısız: {e}")
                host = 'localhost'
        self.milvus_host = host
        self.milvus_port = port
        self.logger.info(f"Milvus bağlantısı: {self.milvus_host}:{self.milvus_port}")
        connections.connect(host=self.milvus_host, port=self.milvus_port)

        # Koleksiyon var mı kontrol et, yoksa oluştur
        if not utility.has_collection(self.collection_name):
            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768),  # Modelinize göre 384 veya 768
                FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=2048),
                FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=512),
                FieldSchema(name="order", dtype=DataType.INT64),
                FieldSchema(name="metadata", dtype=DataType.VARCHAR, max_length=2048)
            ]
            schema = CollectionSchema(fields, description="RAG chunks collection")
            collection = Collection(self.collection_name, schema)
            # Index oluştur
            index_params = {"index_type": "IVF_FLAT", "metric_type": "L2", "params": {"nlist": 128}}
            collection.create_index(field_name="embedding", index_params=index_params)
            collection.load()
            self.logger.info(f"Milvus koleksiyonu oluşturuldu: {self.collection_name}")
        self.collection = Collection(self.collection_name)

    def search(self, query_embedding: Any, top_k: int = 5) -> List[Dict]:
        """
        Milvus ile vektör arama, metadata ile parent chunk çekme.
        """
        self.logger.info(f"Searching Milvus for top {top_k} results")
        if isinstance(query_embedding, list):
            query_embedding = np.array(query_embedding)
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
        results = self.collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            output_fields=["content", "title", "order", "metadata"]
        )
        hits = []
        for hit in results[0]:
            hits.append({
                'score': hit.distance,
                'content': hit.entity.get('content', ''),
                'title': hit.entity.get('title', ''),
                'order': hit.entity.get('order', 0),
                'metadata': hit.entity.get('metadata', {}),
            })
        self.logger.info(f"Found {len(hits)} results")
        return hits 