import logging
import uuid
from typing import Optional, Dict, List
from databases import Database
from backend.models import ModelCreateRequest, ModelCreateResponse, ModelConfigRequest
from backend.config.models import ModelConfig  # Added import for ModelConfig
from backend.config.models import MODEL_TOKEN_LIMITS  # Token limitlerini merkezi configten al

class ModelService:
    def __init__(self, config: ModelConfig, database: Database):
        self.config = config
        self.database = database
        self.logger = logging.getLogger(__name__)

    async def create_model(self, request: ModelCreateRequest) -> ModelCreateResponse:
        """Create a new model configuration"""
        # Check if model with this id already exists
        # (model_id UUID ile oluşturuluyor, çakışma riski yok, duplicate kontrolü gerekmez)
        model_id = str(uuid.uuid4())
        # Get default max_tokens based on model
        default_max_tokens = self._get_default_max_tokens(request.model)
        await self.database.execute(
            """
            INSERT INTO models (
                model_id, provider, model_name, model, 
                system_prompt, api_key, temperature,
                max_tokens, token_limit, is_active,
                knowledge_table_name, knowledge_table_id
            ) VALUES (
                :model_id, :provider, :model_name, :model,
                :system_prompt, :api_key, :temperature,
                :max_tokens, :token_limit, :is_active,
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
                "temperature": request.temperature,
                "max_tokens": request.max_tokens or default_max_tokens,
                "token_limit": request.token_limit,
                "is_active": request.is_active,
                "knowledge_table_name": request.knowledge_table_name,
                "knowledge_table_id": request.knowledge_table_id
            }
        )
        return ModelCreateResponse(
            status="success",
            model_name=request.model_name,
            model_id=model_id
        )

    def _get_default_max_tokens(self, model: str) -> int:
        """Model için varsayılan max_tokens değerini merkezi konfigürasyondan döndürür"""
        model_lower = model.lower()
        for key, limit in MODEL_TOKEN_LIMITS.items():
            if key in model_lower:
                return limit
        return 4000  # Varsayılan değer

    async def get_model_config(self, model_id: str) -> Dict:
        """Get model configuration by ID (model_id zorunlu)"""
        model = await self._get_model_by_id(model_id)
        self.logger.info(f"[get_model_config] DB'den çekilen model: {model}")
        if not model:
            return {
                "provider": self.config.default_provider,
                "model": self.config.default_model,
                "system_prompt": self.config.default_system_prompt,
                "temperature": 0.7,
                "max_tokens": self._get_default_max_tokens(self.config.default_model),
                "token_limit": None,
                "is_active": True
            }
        effective_token_limit = model['token_limit'] or model['max_tokens']
        config_dict = {
            "provider": model['provider'],
            "model": model['model'],
            "system_prompt": model['system_prompt'],
            "api_key": model['api_key'],
            "temperature": model['temperature'],
            "max_tokens": model['max_tokens'],
            "token_limit": model['token_limit'],
            "effective_token_limit": effective_token_limit,
            "is_active": model['is_active'],
            "knowledge_table_name": model['knowledge_table_name'],
            "knowledge_table_id": model['knowledge_table_id']
        }
        self.logger.info(f"[get_model_config] Dönen config dict: {config_dict}")
        return config_dict

    async def _get_model_by_id(self, model_id: str) -> Dict:
        """Internal method to get model by ID"""
        row = await self.database.fetch_one(
            "SELECT * FROM models WHERE model_id = :model_id",
            {"model_id": model_id}
        )
        self.logger.info(f"[_get_model_by_id] DB'den çekilen satır: {row}")
        return dict(row) if row else None

    async def list_models(self) -> List[Dict]:
        """List all registered models"""
        rows = await self.database.fetch_all("SELECT * FROM models")
        return [dict(row) for row in rows]

    async def get_model(self, model_id: str) -> Dict:
        """Get details of a specific model"""
        model = await self._get_model_by_id(model_id)
        if not model:
            raise ValueError(f"Cannot find model with ID: {model_id}")
        return model

    async def update_model(self, model_id: str, update_data: Dict) -> Dict:
        """Update model configuration with partial data"""
        if not update_data:
            raise ValueError("No update data provided")
            
        # Validate fields exist in model
        valid_fields = [
            'model_name', 'model', 'system_prompt', 'api_key',
            'temperature', 'max_tokens', 'token_limit', 'is_active',
            'knowledge_table_name', 'knowledge_table_id'
        ]
        invalid_fields = set(update_data.keys()) - set(valid_fields)
        if invalid_fields:
            raise ValueError(f"Invalid fields for update: {invalid_fields}")
            
        # Token limiti kontrolü
        if 'token_limit' in update_data and update_data['token_limit'] is not None:
            model = await self._get_model_by_id(model_id)
            if not model:
                raise ValueError(f"Model not found: {model_id}")
            
            max_tokens = update_data.get('max_tokens', model['max_tokens'])
            if update_data['token_limit'] > max_tokens:
                raise ValueError(
                    f"Token limit ({update_data['token_limit']}) cannot exceed "
                    f"model's maximum token capacity ({max_tokens})"
                )
            
        set_clause = ", ".join(f"{k} = :{k}" for k in update_data.keys())
        await self.database.execute(
            f"UPDATE models SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE model_id = :model_id",
            {"model_id": model_id, **update_data}
        )
        
        return await self.get_model(model_id)

    async def delete_model(self, model_id: str) -> Dict:
        """Delete a model configuration"""
        model = await self.get_model(model_id)
        await self.database.execute(
            "DELETE FROM models WHERE model_id = :model_id",
            {"model_id": model_id}
        )
        return {"status": "deleted", "model_id": model_id}