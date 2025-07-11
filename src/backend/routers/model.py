from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from ..models import (
    ModelCreateRequest, ModelCreateResponse, ModelConfigRequest,
    ModelProvider, ModelConfig
)
from ..services.model.service import ModelService
from ..database import get_db
from ..auth import get_current_user
from ..models import UserPublic
import logging

router = APIRouter(prefix="/models", tags=["models"])
logger = logging.getLogger(__name__)

@router.post("/", response_model=ModelCreateResponse)
async def create_model(
    request: ModelCreateRequest,
    model_service: ModelService = Depends(get_model_service),
    current_user: UserPublic = Depends(get_current_user)
):
    """Yeni bir model yapılandırması oluştur"""
    logger.info(f"[POST /models/] Create model called: request={request}")
    try:
        # Token limiti kontrolü
        if request.token_limit is not None:
            default_max_tokens = model_service._get_default_max_tokens(request.model)
            max_tokens = request.max_tokens or default_max_tokens
            
            if request.token_limit > max_tokens:
                logger.error(f"[POST /models/] Token limit error: {request.token_limit} > {max_tokens}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Token limit ({request.token_limit}) cannot exceed "
                           f"model's maximum token capacity ({max_tokens})"
                )
        
        result = await model_service.create_model(request)
        logger.info(f"[POST /models/] Success: {result}")
        return result
    except ValueError as e:
        logger.error(f"[POST /models/] ValueError: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[POST /models/] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{model_id}", response_model=ModelConfig)
async def get_model(
    model_id: str,
    model_service: ModelService = Depends(),
    current_user: UserPublic = Depends(get_current_user)
):
    """Model yapılandırmasını getir"""
    logger.info(f"[GET /models/{{model_id}}] Get model called: model_id={model_id}")
    try:
        result = await model_service.get_model(model_id)
        logger.info(f"[GET /models/{{model_id}}] Success: {result}")
        return result
    except ValueError as e:
        logger.error(f"[GET /models/{{model_id}}] ValueError: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"[GET /models/{{model_id}}] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[ModelConfig])
async def list_models(
    model_service: ModelService = Depends(),
    current_user: UserPublic = Depends(get_current_user),
    active_only: bool = True
):
    """Tüm modelleri listele"""
    logger.info(f"[GET /models/] List models called: active_only={active_only}")
    try:
        models = await model_service.list_models()
        if active_only:
            models = [m for m in models if m.get("is_active", True)]
        logger.info(f"[GET /models/] Success: {len(models)} models returned")
        return models
    except Exception as e:
        logger.error(f"[GET /models/] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{model_id}", response_model=ModelConfig)
async def update_model(
    model_id: str,
    update_data: ModelConfigRequest,
    model_service: ModelService = Depends(),
    current_user: UserPublic = Depends(get_current_user)
):
    """Model yapılandırmasını güncelle"""
    logger.info(f"[PATCH /models/{{model_id}}] Update model called: model_id={model_id}, update_data={update_data}")
    try:
        # Token limiti kontrolü
        if update_data.token_limit is not None:
            model = await model_service.get_model(model_id)
            max_tokens = update_data.max_tokens or model.get("max_tokens")
            
            if update_data.token_limit > max_tokens:
                logger.error(f"[PATCH /models/{{model_id}}] Token limit error: {update_data.token_limit} > {max_tokens}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Token limit ({update_data.token_limit}) cannot exceed "
                           f"model's maximum token capacity ({max_tokens})"
                )
        
        result = await model_service.update_model(model_id, update_data.dict(exclude_unset=True))
        logger.info(f"[PATCH /models/{{model_id}}] Success: {result}")
        return result
    except ValueError as e:
        logger.error(f"[PATCH /models/{{model_id}}] ValueError: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[PATCH /models/{{model_id}}] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{model_id}")
async def delete_model(
    model_id: str,
    model_service: ModelService = Depends(),
    current_user: UserPublic = Depends(get_current_user)
):
    """Model yapılandırmasını sil"""
    logger.info(f"[DELETE /models/{{model_id}}] Delete model called: model_id={model_id}")
    try:
        result = await model_service.delete_model(model_id)
        logger.info(f"[DELETE /models/{{model_id}}] Success: {result}")
        return result
    except ValueError as e:
        logger.error(f"[DELETE /models/{{model_id}}] ValueError: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"[DELETE /models/{{model_id}}] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 