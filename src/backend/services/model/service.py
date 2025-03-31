import logging
import uuid
from typing import Optional, Dict
from databases import Database
from models import ModelCreateRequest, ModelCreateResponse, ModelConfigRequest
from .config import ModelConfig  # Added import for ModelConfig

class ModelService:
    def __init__(self, config: ModelConfig, database: Database):
        self.config = config
        self.database = database
        self.logger = logging.getLogger(__name__)

    async def create_model(self, request: ModelCreateRequest) -> ModelCreateResponse:
        """Create a new model configuration"""
        # Check if model with this name already exists
        existing_model = await self._get_model_by_name(request.model_name)
        if existing_model:
            return ModelCreateResponse(
                status="error",
                model_name=request.model_name,
                model_id="",
                error=f"Model with name '{request.model_name}' already exists"
            )
            
        model_id = str(uuid.uuid4())
        
        await self.database.execute(
            """
            INSERT INTO models (
                model_id, provider, model_name, model, 
                system_prompt, api_key, 
                knowledge_table_name, knowledge_table_id
            ) VALUES (
                :model_id, :provider, :model_name, :model,
                :system_prompt, :api_key,
                :knowledge_table_name, :knowledge_table_id
            )
            """,
            {
                "model_id": model_id,
                "provider": request.provider.value,
                "model_name": request.model_name,
                "model": request.model,
                "system_prompt": request.system_prompt,
                "api_key": request.api_key,
                "knowledge_table_name": request.knowledge_table_name,
                "knowledge_table_id": request.knowledge_table_id
            }
        )
        
        return ModelCreateResponse(
            status="success",
            model_name=request.model_name,
            model_id=model_id
        )

    async def get_model_config(self, model_id: Optional[str] = None, 
                             model_name: Optional[str] = None) -> Dict:
        """Get model configuration by ID or name"""
        if model_id:
            return await self._get_model_by_id(model_id)
        elif model_name:
            return await self._get_model_by_name(model_name)
        else:
            return {
                "provider": self.config.default_provider,
                "model": self.config.default_model,
                "system_prompt": self.config.default_system_prompt
            }

    async def _get_model_by_id(self, model_id: str) -> Dict:
        """Internal method to get model by ID"""
        row = await self.database.fetch_one(
            "SELECT * FROM models WHERE model_id = :model_id",
            {"model_id": model_id}
        )
        return dict(row) if row else None

    async def _get_model_by_name(self, model_name: str) -> Dict:
        """Internal method to get model by name"""
        row = await self.database.fetch_one(
            "SELECT * FROM models WHERE model_name = :model_name",
            {"model_name": model_name}
        )
        return dict(row) if row else None