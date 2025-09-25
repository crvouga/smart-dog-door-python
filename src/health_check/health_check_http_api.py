from fastapi import APIRouter
import logging


class HealthCheckHttpApi:
    _logger: logging.Logger

    def __init__(self, logger: logging.Logger):
        self._logger = logger.getChild("health_check_http_api")
        self.api_router = APIRouter()

        @self.api_router.get("/health")
        async def health_check():
            self._logger.info("Health check requested")
            return {"status": "ok"}
