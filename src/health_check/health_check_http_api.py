import logging
from typing import Dict
from src.shared.http_api import HttpApi


class HealthCheckHttpApi(HttpApi):
    def __init__(self, logger: logging.Logger):
        super().__init__(logger=logger)

        @self.api_router.get("/health")
        async def health_check() -> Dict[str, str]:
            self.logger.info("Health check requested")
            return {"status": "ok"}
