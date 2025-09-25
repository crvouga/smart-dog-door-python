import asyncio
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import uvicorn
from src.library.life_cycle import LifeCycle
import logging
from src.health_check.health_check_http_api import HealthCheckHttpApi
from src.login.login_link_http_api import LoginLinkHttpApi
from src.login.login_link_db import LoginLinkDb
from src.library.sql_db import SqlDb
from src.shared.send_email.send_email_impl import SendEmailImpl
from src.shared.send_email.send_email_interface import SendEmail
from src.shared.result_page.result_page_http_api import ResultPageHttpApi
from src.shared.http_api import HttpApi


class AppHttpApi(LifeCycle):
    logger: logging.Logger
    app: FastAPI
    _server: uvicorn.Server
    sql_db: SqlDb
    send_email: SendEmail

    def __init__(self) -> None:
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("app")
        self.app = FastAPI()
        self.sql_db = SqlDb(db_path="app.db")
        self.send_email = SendEmailImpl.init(logger=self.logger)

        http_apis: list[HttpApi] = [
            HealthCheckHttpApi(logger=self.logger),
            LoginLinkHttpApi(
                logger=self.logger, sql_db=self.sql_db, send_email=self.send_email
            ),
            ResultPageHttpApi(logger=self.logger),
        ]

        for http_api in http_apis:
            self.app.include_router(http_api.api_router)

        @self.app.get("/")
        def default_router() -> RedirectResponse:
            return RedirectResponse(url="/login_link__send", status_code=303)

        config = uvicorn.Config(self.app, host="0.0.0.0", port=8000, log_level="info")
        self._server = uvicorn.Server(config)

    async def start(self) -> None:
        self.logger.info("Starting server on port 8000")
        self.logger.info("Initializing database...")
        login_link_db = LoginLinkDb(sql_db=self.sql_db)
        async with self.sql_db.transaction() as tx:
            for up_sql in login_link_db.up():
                await tx.execute(up_sql, ())
        self.logger.info("Database initialized successfully")
        await self._server.serve()

    async def stop(self) -> None:
        self.logger.info("Stopping server")
        self._server.should_exit = True
