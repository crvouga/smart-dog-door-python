from typing import Any
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
import uvicorn
from src.library.life_cycle import LifeCycle
import logging
from src.health_check.health_check_http_api import HealthCheckHttpApi
from src.login.login_link_http_api import LoginLinkHttpApi
from src.shared.result_page.result_page_http_api import ResultPageHttpApi
from src.shared.http_api import HttpApi
from src.shared.send_email.sent_emails_http_api import SentEmailsHttpApi
from src.library.new_id import new_id
from starlette.middleware.base import BaseHTTPMiddleware
from src.library.sql_db import SqlDb
from src.login.login_link_db import LoginLinkDb
from src.shared.send_email.email_db import EmailDb
from src.user.user_db import UserDb
from src.user.user_session_db import UserSessionDb


class AppHttpApi(LifeCycle):
    def __init__(self) -> None:
        logging.basicConfig(level=logging.INFO)
        self.app = FastAPI()

        self.kwargs: dict[str, Any] = {}
        self.logger = logging.getLogger("app")
        self.kwargs["logger"] = self.logger
        self.sql_db = SqlDb(db_path="main.db")
        self.kwargs["sql_db"] = self.sql_db

        async def session_middleware(request: Request, call_next):
            if not request.cookies.get("session_id"):
                response = await call_next(request)
                response.set_cookie(
                    key="session_id", value=new_id("session__"), httponly=True
                )
                return response
            return await call_next(request)

        self.app.add_middleware(BaseHTTPMiddleware, dispatch=session_middleware)

        http_apis: list[HttpApi] = [
            HealthCheckHttpApi(**self.kwargs),
            LoginLinkHttpApi(**self.kwargs),
            ResultPageHttpApi(**self.kwargs),
            SentEmailsHttpApi(**self.kwargs),
        ]

        for http_api in http_apis:
            self.app.include_router(http_api.api_router)

        @self.app.get("/")
        async def default_router(path: str) -> RedirectResponse:
            return RedirectResponse(url="/login_link__send", status_code=303)

        config = uvicorn.Config(self.app, host="0.0.0.0", port=8000, log_level="info")
        self._server = uvicorn.Server(config)

    def start(self) -> None:
        self.logger.info("Starting server on port 8000")
        import asyncio

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
