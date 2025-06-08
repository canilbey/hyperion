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
                         model: str,
                         model_name: str,
                         system_prompt: str,
                         api_key: Optional[str] = None,
                         knowledge_table_name: Optional[str] = None,
                         knowledge_table_id: Optional[str] = None) -> dict:
        try:
            # Check for duplicate model name
            existing = await self.database.fetch_one(
                "SELECT model_id FROM models WHERE model_name = :model_name",
                {"model_name": model_name}
            )
            if existing:
                raise HTTPException(
                    status_code=400,
                    detail=f"Model with name '{model_name}' already exists"
                )

            model_id = str(uuid.uuid4())
            
            await self.database.execute(
                """
                INSERT INTO models (
                    model_id,
                    provider,
                    model,
                    model_name,
                    system_prompt,
                    api_key,
                    knowledge_table_name,
                    knowledge_table_id
                ) VALUES (:model_id, :provider, :model, :model_name, :system_prompt, :api_key,
                         :knowledge_table_name, :knowledge_table_id)
                """,
                {
                    "model_id": model_id,
                    "provider": provider.value,
                    "model": model,
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

    async def get_model_config(self, model_id: Optional[str] = None, model_name: Optional[str] = None) -> ModelConfig:
        try:
            if not model_id and not model_name:
                raise HTTPException(
                    status_code=400,
                    detail="Either model_id or model_name must be provided"
                )

            logger.info("Loading model config", extra={
                "event": "model_config_load",
                "model_id": model_id,
                "model_name": model_name
            })

            if model_id:
                model = await self.database.fetch_one(
                    "SELECT * FROM models WHERE model_id = :model_id",
                    {"model_id": model_id}
                )
            else:
                model = await self.database.fetch_one(
                    "SELECT * FROM models WHERE model_name = :model_name",
                    {"model_name": model_name}
                )

            if not model:
                error_msg = f"Model {'with id ' + model_id if model_id else 'named ' + model_name} not found"
                logger.error(error_msg)
                raise HTTPException(
                    status_code=404,
                    detail=error_msg
                )
            
            logger.info("Found model in database", extra={
                "event": "model_found",
                "model_data": {
                    "provider": model["provider"],
                    "model": model["model"],
                    "has_api_key": bool(model["api_key"]),
                    "has_knowledge_table": bool(model["knowledge_table_name"])
                }
            })

            config = ModelConfig(
                provider=ModelProvider(model["provider"]),
                model=model["model"],
                api_key=model["api_key"],
                knowledge_table=model["knowledge_table_name"],
                temperature=0.7
            )

            logger.info("Created ModelConfig", extra={
                "event": "model_config_created",
                "config": {
                    "provider": config.provider.value,
                    "model": config.model,
                    "has_api_key": bool(config.api_key),
                    "temperature": config.temperature
                }
            })

            return config
        except Exception as e:
            logger.error(f"Error loading model config: {str(e)}", exc_info=True)
            raise