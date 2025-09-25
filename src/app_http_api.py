from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import uvicorn
from src.library.life_cycle import LifeCycle
import logging
from src.health_check.health_check_http_api import HealthCheckHttpApi
from src.login.login_link_http_api import LoginLinkHttpApi
from src.library.sql_db import SqlDb
from src.shared.send_email.send_email_impl import SendEmailImpl
from src.shared.send_email.send_email_interface import SendEmail
from src.shared.result_page.result_page import ResultPage


class AppHttpApi(LifeCycle):
    _logger: logging.Logger
    _app: FastAPI
    _server: uvicorn.Server
    _sql_db: SqlDb
    _send_email: SendEmail

    def __init__(self) -> None:
        logging.basicConfig(level=logging.INFO)
        self._logger = logging.getLogger("app")
        self._app = FastAPI()
        self._sql_db = SqlDb(db_path="sqlite:///app.db")
        self._send_email = SendEmailImpl.init(logger=self._logger)

        self._app.include_router(HealthCheckHttpApi(logger=self._logger).api_router)
        self._app.include_router(
            LoginLinkHttpApi(
                logger=self._logger, sql_db=self._sql_db, send_email=self._send_email
            ).api_router
        )
        self._app.include_router(ResultPage(logger=self._logger).api_router)

        @self._app.get("/")
        def default_router():
            return RedirectResponse(url="/login_link.send", status_code=303)

        config = uvicorn.Config(self._app, host="0.0.0.0", port=8000, log_level="info")
        self._server = uvicorn.Server(config)

    def start(self) -> None:
        self._logger.info("Starting server on port 8000")
        self._server.run()

    def stop(self) -> None:
        self._logger.info("Stopping server")
        self._server.should_exit = True
