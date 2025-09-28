from typing import Dict
from src.shared.http_api import HttpApi
from fastapi import APIRouter
import logging


class HealthCheckHttpApi(HttpApi):
    def __init__(self, **kwargs):
        super().__init__()
        self.logger = kwargs.get("logger")
        assert isinstance(self.logger, logging.Logger)

        @self.api_router.get("/health")
        async def health_check() -> Dict[str, str]:
            self.logger.info("Health check requested")
            return {"status": "ok"}
