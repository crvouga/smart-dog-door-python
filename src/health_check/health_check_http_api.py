from typing import Dict
from src.shared.http_api import HttpApi
from src.ctx import Ctx


class HealthCheckHttpApi(HttpApi):
    def __init__(self, ctx: Ctx):
        super().__init__(ctx=ctx)

        @self.api_router.get("/health")
        async def health_check() -> Dict[str, str]:
            self.logger.info("Health check requested")
            return {"status": "ok"}
