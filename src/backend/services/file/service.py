import logging
import os
import uuid
from typing import Optional
from backend.models import FileUploadResponse, TextChunk, FileMetadata
from .config import FileConfig  # Added import for FileConfig
import PyPDF2
from databases import Database

class FileService:
    def __init__(self, config: FileConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)

    async def handle_file_upload(self, file, upload_dir: str, db: Database, user_id: Optional[str] = None) -> FileUploadResponse:
        """Handle file upload with validation, parsing, and metadata DB insert"""
        try:
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

            # --- Dosya parsing işlemi ---
            text_chunks = self.parse_file(file_id, file_path, file.content_type)
            self.logger.info(f"Parsed {len(text_chunks)} text chunks from uploaded file {file.filename}")

            # Chunk toplam boyutunu hesapla
            chunked_total_size = sum(len(chunk.text.encode("utf-8")) for chunk in text_chunks)
            num_chunks = len(text_chunks)

            # Metadata'yı files tablosuna ekle
            insert_query = """
            INSERT INTO files (file_id, original_filename, content_type, original_size, num_chunks, chunked_total_size, user_id)
            VALUES (:file_id, :original_filename, :content_type, :original_size, :num_chunks, :chunked_total_size, :user_id)
            RETURNING upload_time
            """
            values = {
                "file_id": file_id,
                "original_filename": file.filename,
                "content_type": file.content_type,
                "original_size": len(contents),
                "num_chunks": num_chunks,
                "chunked_total_size": chunked_total_size,
                "user_id": user_id
            }
            row = await db.fetch_one(insert_query, values)
            upload_time = row[0] if row else None

            return FileUploadResponse(
                file_id=file_id,
                filename=file.filename,
                content_type=file.content_type,
                size=len(contents),
                num_chunks=num_chunks,
                chunked_total_size=chunked_total_size,
                upload_time=upload_time,
                user_id=user_id
            )
        except Exception as e:
            self.logger.error(f"File upload failed: {str(e)}")
            raise

    def parse_file(self, file_id: str, file_path: str, content_type: str):
        """Dosya tipine göre uygun parser ile metin çıkarımı yapar ve TextChunk listesi döner."""
        if content_type == "application/pdf":
            return self.parse_pdf(file_id, file_path)
        elif content_type == "text/plain":
            return self.parse_txt(file_id, file_path)
        else:
            self.logger.warning(f"No parser implemented for content_type: {content_type}")
            return []

    def parse_pdf(self, file_id: str, file_path: str):
        """PDF dosyasını sayfa sayfa TextChunk olarak döndürür."""
        chunks = []
        try:
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for idx, page in enumerate(reader.pages):
                    text = page.extract_text()
                    if text:
                        chunks.append(TextChunk(file_id=file_id, chunk_index=idx, text=text))
        except Exception as e:
            self.logger.error(f"PDF parsing failed: {e}")
        return chunks

    def parse_txt(self, file_id: str, file_path: str):
        """TXT dosyasını satır satır TextChunk olarak döndürür."""
        chunks = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for idx, line in enumerate(f):
                    line = line.strip()
                    if line:
                        chunks.append(TextChunk(file_id=file_id, chunk_index=idx, text=line))
        except Exception as e:
            self.logger.error(f"TXT parsing failed: {e}")
        return chunks

    async def save_text_chunks(self, db: Database, chunks: list[TextChunk]):
        """TextChunk listesini veritabanına toplu ekler."""
        if not chunks:
            return
        query = """
        INSERT INTO text_chunks (file_id, chunk_index, text, metadata)
        VALUES (:file_id, :chunk_index, :text, :metadata)
        """
        values = [
            {
                "file_id": c.file_id,
                "chunk_index": c.chunk_index,
                "text": c.text,
                "metadata": c.metadata if c.metadata is not None else None
            }
            for c in chunks
        ]
        await db.execute_many(query=query, values=values)
        self.logger.info(f"Saved {len(chunks)} text chunks to database for file_id={chunks[0].file_id}")