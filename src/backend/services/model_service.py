import uuid
import logging
from typing import Optional
from databases import Database
from fastapi import HTTPException
from config.models import ModelProvider, ModelConfig

logger = logging.getLogger(__name__)

class ModelService:
    def __init__(self, database: Database):
        self.database = database

    async def create_model(self, 
                         provider: ModelProvider,
                         model_name: str,
                         system_prompt: str,
                         api_key: Optional[str] = None,
                         knowledge_table_name: Optional[str] = None,
                         knowledge_table_id: Optional[str] = None) -> dict:
        try:
            model_id = str(uuid.uuid4())
            
            await self.database.execute(
                """
                INSERT INTO models (
                    model_id,
                    provider,
                    model_name,
                    system_prompt,
                    api_key,
                    knowledge_table_name,
                    knowledge_table_id
                ) VALUES (:model_id, :provider, :model_name, :system_prompt, :api_key,
                         :knowledge_table_name, :knowledge_table_id)
                """,
                {
                    "model_id": model_id,
                    "provider": provider.value,
                    "model_name": model_name,
                    "system_prompt": system_prompt,
                    "api_key": api_key,
                    "knowledge_table_name": knowledge_table_name,
                    "knowledge_table_id": knowledge_table_id
                }
            )
            
            return {
                "status": "model created",
                "model_name": model_name,
                "model_id": model_id
            }
        except Exception as e:
            logger.error(f"Model creation failed: {str(e)}")
            raise HTTPException(status_code=500, detail="Model creation failed")

    async def get_model_config(self, model_id: str) -> ModelConfig:
        model = await self.database.fetch_one(
            "SELECT * FROM models WHERE model_id = :model_id",
            {"model_id": model_id}
        )
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        
        return ModelConfig(
            provider=ModelProvider(model["provider"]),
            model=model["model_name"],
            api_key=model["api_key"],
            knowledge_table=model["knowledge_table_name"],
            temperature=0.7
        )