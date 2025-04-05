from src.client_console.client_console import ConsoleClient
from src.client_desktop.client_desktop import DesktopClient
import logging
import time
from src.library.life_cycle import LifeCycle


import sys


class Main:
    _logger: logging.Logger
    _resources: list[LifeCycle]
    _client: LifeCycle

    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger.getChild("main")
        client = DesktopClient(logger=self._logger)
        self._client = client
        self._resources = [client]

    def start(self) -> None:
        for resource in self._resources:
            resource.start()

    def run(self) -> int:
        """Runs the main blocking part of the application."""
        if hasattr(self._client, "run"):

            return self._client.run()
        else:

            self._logger.info("Client has no run method, entering wait loop.")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                self._logger.info("KeyboardInterrupt received in main loop.")
                return 0

    def stop(self) -> None:
        for resource in reversed(self._resources):
            resource.stop()


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()

    main_app = Main(logger=logger)
    main_app.start()

    exit_code = main_app.run()

    main_app.stop()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
