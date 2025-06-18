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
from backend.services.chunking.parent_child_chunker import chunk_elements
from backend.services.milvus_service import MilvusService
from backend.services.evaluation.logger import log_search
import traceback
from backend.services.file.pdf_adapter import extract_pdf_document

class FileService:
    def __init__(self, config: FileConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)

    async def handle_file_upload(self, file, upload_dir: str, db: Database, user_id: Optional[str] = None) -> FileUploadResponse:
        """Yeni pipeline: unstructured + parent-child chunking + embedding + Milvus + detaylı loglama"""
        try:
            # Safe filename encoding - EN BAŞTA TANIMLA
            try:
                safe_filename = safe_utf8(file.filename)
            except Exception as e:
                self.logger.error(f"Filename decode error: {e}, filename: {file.filename}")
                traceback.print_exc()
                safe_filename = "ERROR"
            
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
            parent_chunks, child_chunks = extract_pdf_document(file_path)
            # Parent chunk'ların content'ini child chunk'ların birleştirilmiş metniyle doldur
            parent_chunks = fill_parent_chunk_content(parent_chunks, child_chunks)

            # Parent chunk'ları kaydet
            parent_id_map = {}
            for parent in parent_chunks:
                insert_query = """
                INSERT INTO parent_chunks (document_id, title, content, "order", metadata)
                VALUES (:document_id, :title, :content, :order, :metadata)
                RETURNING id
                """
                safe_title = safe_utf8(parent["title"])
                # Parent content'i zaten fill_parent_chunk_content ile güvenli
                safe_content = safe_utf8(parent["content"])
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
                # Safe child content encoding ve filtreleme
                try:
                    safe_child_content = safe_utf8(child["content"])
                except Exception as e:
                    self.logger.error(f"Child chunk decode error: {e}, content: {child['content']}")
                    traceback.print_exc()
                    safe_child_content = "ERROR"
                if not safe_child_content or not safe_child_content.strip() or not all(c.isprintable() for c in safe_child_content):
                    continue  # Boş veya bozuk içerik kaydetme
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
            
            # Dosya metadata'sını files tablosuna ekle
            try:
                insert_query = """
                INSERT INTO files (file_id, original_filename, content_type, original_size, num_chunks, chunked_total_size, upload_time, user_id)
                VALUES (:file_id, :original_filename, :content_type, :original_size, :num_chunks, :chunked_total_size, :upload_time, :user_id)
                """
                try:
                    safe_filename = safe_ascii_filename(file.filename)
                except Exception as e:
                    self.logger.error(f"Files table filename decode error: {e}, filename: {file.filename}")
                    traceback.print_exc()
                    safe_filename = "ERROR_FILENAME"
                values = {
                    "file_id": file_id,
                    "original_filename": safe_filename,
                    "content_type": file.content_type,
                    "original_size": len(contents),
                    "num_chunks": len(child_chunks),
                    "chunked_total_size": safe_total_size,
                    "upload_time": datetime.now(timezone.utc),
                    "user_id": user_id
                }
                await db.execute(insert_query, values)
            except Exception as e:
                self.logger.error(f"Files table insert error: {e}, values: {values}")
                traceback.print_exc()

            return FileUploadResponse(
                file_id=file_id,
                filename=safe_ascii_filename(file.filename),
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

def fill_parent_chunk_content(parent_chunks, child_chunks):
    """
    Her parent chunk'ın content alanını, o parent'a bağlı child chunk'ların content'lerinin birleştirilmiş haliyle doldurur.
    """
    parent_map = {p["id"]: p for p in parent_chunks}
    for p in parent_chunks:
        p["content"] = "\n".join([c["content"] for c in child_chunks if c.get("parent_id") == p["id"] and c.get("content")])
    return parent_chunks

def safe_utf8(text):
    try:
        return text.encode("utf-8", errors="replace").decode("utf-8")
    except Exception:
        return ""

def safe_ascii_filename(filename):
    import re
    return re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)