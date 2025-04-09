from src.client_desktop.client_desktop import DesktopClient
import logging
from src.env import Env
from src.library.life_cycle import LifeCycle


class App(LifeCycle):
    _logger: logging.Logger
    _client: LifeCycle

    def __init__(self) -> None:
        logging.basicConfig(level=logging.INFO)

        self._logger = logging.getLogger("app")

        env = Env.load()

        self._client = DesktopClient(
            env=env,
            logger=self._logger,
        )

    def start(self) -> None:
        self._logger.info("Starting")
        self._client.start()
        self._logger.info("Started")

    def stop(self) -> None:
        self._logger.info("Stopping")
        self._client.stop()
        self._logger.info("Stopped")
