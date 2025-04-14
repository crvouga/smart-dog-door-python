import signal
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

        # Set up signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, sig, frame):
        """Handle SIGINT gracefully."""
        self._logger.info("SIGINT received, stopping application...")
        self.stop()

    def start(self) -> None:
        self._logger.info("Starting")
        self._client.start()
        self._logger.info("Started")

    def stop(self) -> None:
        self._logger.info("Stopping")
        self._client.stop()
        self._logger.info("Stopped")
