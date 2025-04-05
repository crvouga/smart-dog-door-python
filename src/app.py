from src.client_console.client_console import ConsoleClient
from src.client_desktop.client_desktop import DesktopClient
import logging
from src.library.life_cycle import LifeCycle

logging.basicConfig(level=logging.INFO)


class App(LifeCycle):
    _logger: logging.Logger
    _client: LifeCycle

    def __init__(
        self,
    ) -> None:
        self._logger = logging.getLogger("app")
        self._client = DesktopClient(logger=self._logger)

    def start(self) -> None:
        self._logger.info("Starting")
        self._client.start()
        self._logger.info("Started")

    def stop(self) -> None:
        self._logger.info("Stopping")
        self._client.stop()
        self._logger.info("Stopped")
