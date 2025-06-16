import logging
import os
import uuid
from typing import Optional
from datetime import datetime, timezone
from backend.models import FileUploadResponse
from .config import FileConfig
from databases import Database
import json
from backend.services.embedding.model_loader import load_embedding_model
from backend.services.embedding.pipeline import embed_chunks
from backend.services.file.unstructured_adapter import parse_document
from backend.services.chunking.parent_child_chunker import chunk_elements
from backend.services.milvus_service import MilvusService
from backend.services.evaluation.logger import log_search

class FileService:
    def __init__(self, config: FileConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)

    async def handle_file_upload(self, file, upload_dir: str, db: Database, user_id: Optional[str] = None) -> FileUploadResponse:
        """Yeni pipeline: unstructured + parent-child chunking + embedding + Milvus + detaylı loglama"""
        try:
            # Safe filename encoding - EN BAŞTA TANIMLA
            safe_filename = file.filename
            if isinstance(safe_filename, str):
                safe_filename = safe_filename.encode('utf-8', errors='ignore').decode('utf-8')
            
            # Validate file type
            if file.content_type not in self.config.allowed_types:
                raise ValueError(f"Unsupported file type: {file.content_type}")

            # Validate file size
            contents = await file.read()
            if len(contents) > self.config.max_file_size:
                raise ValueError(f"File size exceeds maximum allowed {self.config.max_file_size} bytes")

            # Save file
            file_id = str(uuid.uuid4())
            file_path = os.path.join(upload_dir, file_id)
            with open(file_path, "wb") as f:
                f.write(contents)

            # --- Yeni pipeline ---
            elements = parse_document(file_path)
            parent_chunks, child_chunks = chunk_elements(elements)

            # Parent chunk'ları kaydet
            parent_id_map = {}
            for parent in parent_chunks:
                insert_query = """
                INSERT INTO parent_chunks (document_id, title, content, "order", metadata)
                VALUES (:document_id, :title, :content, :order, :metadata)
                RETURNING id
                """
                # Safe JSON serialization
                safe_title = parent["title"]
                safe_content = parent["content"]
                if isinstance(safe_title, str):
                    safe_title = safe_title.encode('utf-8', errors='ignore').decode('utf-8')
                if isinstance(safe_content, str):
                    safe_content = safe_content.encode('utf-8', errors='ignore').decode('utf-8')
                
                values = {
                    "document_id": file_id,
                    "title": safe_title,
                    "content": safe_content,
                    "order": parent["order"],
                    "metadata": json.dumps(parent.get("metadata", {}), ensure_ascii=True)
                }
                row = await db.fetch_one(insert_query, values)
                parent_id = row[0] if row else None
                parent_id_map[parent["id"]] = parent_id

            # Child chunk'ları kaydet
            for child in child_chunks:
                insert_query = """
                INSERT INTO child_chunks (parent_id, content, type, "order", metadata)
                VALUES (:parent_id, :content, :type, :order, :metadata)
                RETURNING id
                """
                # Safe child content encoding
                safe_child_content = child["content"]
                if isinstance(safe_child_content, str):
                    safe_child_content = safe_child_content.encode('utf-8', errors='ignore').decode('utf-8')
                
                values = {
                    "parent_id": parent_id_map[child["parent_id"]],
                    "content": safe_child_content,
                    "type": child.get("type"),
                    "order": child.get("order"),
                    "metadata": json.dumps(child.get("metadata", {}), ensure_ascii=True)
                }
                row = await db.fetch_one(insert_query, values)
                child["db_id"] = row[0] if row else None

            # Child chunk embedding ve Milvus'a ekleme
            embedding_model = load_embedding_model("paraphrase-multilingual-MiniLM-L12-v2")
            embeddings = embed_chunks(child_chunks, model_name="paraphrase-multilingual-MiniLM-L12-v2")
            milvus_service = MilvusService()
            for child, embedding in zip(child_chunks, embeddings):
                metadata = {
                    "parent_id": parent_id_map[child["parent_id"]],
                    "type": child.get("type"),
                    "order": child.get("order"),
                    "metadata": child.get("metadata", {})
                }
                # Safe metadata for Milvus
                try:
                    safe_metadata_str = json.dumps(metadata, ensure_ascii=True)
                except Exception as e:
                    # Fallback metadata if JSON serialization fails
                    safe_metadata_str = json.dumps({
                        "parent_id": metadata.get("parent_id", "unknown"),
                        "type": str(metadata.get("type", "text")),
                        "order": metadata.get("order", 0),
                        "encoding_error": str(e)
                    }, ensure_ascii=True)
                
                milvus_service.insert_embedding(embedding, safe_metadata_str)

            # Detaylı loglama - safe metadata
            try:
                safe_log_metadata = {
                    "file_id": file_id,
                    "filename": safe_filename,
                    "parent_chunks_count": len(parent_chunks),
                    "child_chunks_count": len(child_chunks),
                    "embeddings": len(embeddings)
                }
                log_search(
                    query="[UPLOAD]",
                    results=[],
                    metadata=safe_log_metadata
                )
            except Exception as log_error:
                self.logger.warning(f"Logging failed: {str(log_error)}")

            # Safe chunk size calculation
            safe_total_size = 0
            for c in child_chunks:
                try:
                    content = c.get("content", "")
                    # Clean content aynı embedding pipeline'daki gibi
                    if isinstance(content, str):
                        # Sadece güvenli karakterleri tut
                        clean_content = ''.join(char for char in content if ord(char) < 127 or char.isalnum() or char.isspace())
                        safe_total_size += len(clean_content.encode("utf-8", errors="ignore"))
                    else:
                        safe_total_size += len(str(content).encode("utf-8", errors="ignore"))
                except Exception:
                    # Hata durumunda estimate değer ekle
                    safe_total_size += 100
            
            return FileUploadResponse(
                file_id=file_id,
                filename=safe_filename,
                content_type=file.content_type,
                size=len(contents),
                num_chunks=len(child_chunks),
                chunked_total_size=safe_total_size,
                upload_time=datetime.now(timezone.utc),
                user_id=user_id
            )
        except Exception as e:
            self.logger.error(f"File upload failed: {str(e)}")
            raise