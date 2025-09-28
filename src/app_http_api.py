import asyncio
from typing import Any
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
from starlette.middleware.base import BaseHTTPMiddleware
from src.library.sql_db import SqlDb
from src.login.login_link_db import LoginLinkDb
from src.shared.send_email.email_db import EmailDb
from src.user.user_db import UserDb
from src.user.user_session_db import UserSessionDb
from src.library.session_id.session_id_set_cookie_middleware import (
    session_id_set_cookie_middleware,
)


class AppHttpApi(LifeCycle):
    def __init__(self) -> None:
        logging.basicConfig(level=logging.INFO)

        self.kwargs: dict[str, Any] = {}
        self.logger = logging.getLogger("app")
        self.kwargs["logger"] = self.logger
        self.sql_db = SqlDb(db_path="main.db")
        self.kwargs["sql_db"] = self.sql_db

        http_apis: list[HttpApi] = [
            HealthCheckHttpApi(**self.kwargs),
            LoginLinkHttpApi(**self.kwargs),
            ResultPageHttpApi(**self.kwargs),
            SentEmailsHttpApi(**self.kwargs),
        ]

        self.app = FastAPI()
        self.app.add_middleware(
            BaseHTTPMiddleware, dispatch=session_id_set_cookie_middleware
        )
        for http_api in http_apis:
            self.app.include_router(http_api.api_router)

        @self.app.get("/")
        async def root() -> RedirectResponse:
            return RedirectResponse(url="/login_link__send", status_code=303)

        self._server_config = uvicorn.Config(
            self.app, host="0.0.0.0", port=8000, log_level="info"
        )
        self._server = uvicorn.Server(self._server_config)

    def start(self) -> None:
        self.logger.info("Starting server on port 8000")

        asyncio.run(self._start_async())

    async def _start_async(self) -> None:
        self.logger.info("Running database migrations...")
        sql_db = self.kwargs["sql_db"]
        assert isinstance(sql_db, SqlDb)
        async with sql_db.transaction() as tx:
            await LoginLinkDb.up(tx=tx)
            await EmailDb.up(tx=tx)
            await UserDb.up(tx=tx)
            await UserSessionDb.up(tx=tx)
        self.logger.info("Database migrations completed successfully")
        await self._server.serve()

    def stop(self) -> None:
        self.logger.info("Stopping server")
        self._server.should_exit = True
