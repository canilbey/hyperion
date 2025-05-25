import logging
import os
import uuid
from typing import Optional
from backend.models import FileUploadResponse
from .config import FileConfig  # Added import for FileConfig

class FileService:
    def __init__(self, config: FileConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)

    async def handle_file_upload(self, file, upload_dir: str) -> FileUploadResponse:
        """Handle file upload with validation"""
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

            return FileUploadResponse(
                file_id=file_id,
                filename=file.filename,
                content_type=file.content_type,
                size=len(contents)
            )

        except Exception as e:
            self.logger.error(f"File upload failed: {str(e)}")
            raise