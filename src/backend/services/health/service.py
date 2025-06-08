import logging
from typing import Dict
from backend.models import HealthCheckResponse
from .config import HealthConfig
from backend.services.core.init_service import InitService

class HealthService:
    def __init__(self, config: HealthConfig, init_service: InitService):
        self.config = config
        self.init_service = init_service
        self.logger = logging.getLogger(__name__)

    async def check_health(self) -> HealthCheckResponse:
        """Check health of all services"""
        try:
            health_status = await self.init_service.health_check()
            return HealthCheckResponse(
                status="healthy",
                database=health_status["database"],
                redis=health_status["redis"]
            )
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return HealthCheckResponse(
                status="unhealthy",
                database="error",
                redis="error"
            )