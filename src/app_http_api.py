from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import uvicorn
from src.library.life_cycle import LifeCycle
import logging
from src.health_check.health_check_http_api import HealthCheckHttpApi
from src.login.login_link_http_api import LoginLinkHttpApi
from src.shared.result_page.result_page_http_api import ResultPageHttpApi
from src.shared.http_api import HttpApi
from src.shared.send_email.sent_emails_http_api import SentEmailsHttpApi
from src.ctx import Ctx


class AppHttpApi(LifeCycle):
    def __init__(self) -> None:
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("app")
        self.app = FastAPI()
        self.ctx = Ctx(logger=self.logger)

        http_apis: list[HttpApi] = [
            HealthCheckHttpApi(ctx=self.ctx),
            LoginLinkHttpApi(ctx=self.ctx),
            ResultPageHttpApi(ctx=self.ctx),
            SentEmailsHttpApi(ctx=self.ctx),
        ]

        for http_api in http_apis:
            self.app.include_router(http_api.api_router)

        @self.app.get("/")
        def default_router(path: str) -> RedirectResponse:
            return RedirectResponse(url="/login_link__send", status_code=303)

        config = uvicorn.Config(self.app, host="0.0.0.0", port=8000, log_level="info")
        self._server = uvicorn.Server(config)

    def start(self) -> None:
        self.logger.info("Starting server on port 8000")
        import asyncio

        asyncio.run(self._start_async())

    async def _start_async(self) -> None:
        self.logger.info("Running database migrations...")
        async with self.ctx.sql_db.transaction() as tx:
            for s in self.ctx.login_link_db.up():
                await tx.execute(s, ())
            for s in self.ctx.email_db.up():
                await tx.execute(s, ())
            for s in self.ctx.user_db.up():
                await tx.execute(s, ())
            for s in self.ctx.user_session_db.up():
                await tx.execute(s, ())
        self.logger.info("Database migrations completed successfully")
        await self._server.serve()

    def stop(self) -> None:
        self.logger.info("Stopping server")
        self._server.should_exit = True
