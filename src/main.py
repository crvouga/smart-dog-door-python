from src.client_console.client_console import ConsoleClient
from src.client_desktop.client_desktop import DesktopClient
import logging
import time
from src.library.life_cycle import LifeCycle


class Main:
    _logger: logging.Logger
    _resources: list[LifeCycle]

    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger.getChild("main")
        self._resources = []

        self._resources.append(ConsoleClient(logger=self._logger))
        if False:
            self._resources.append(DesktopClient(logger=self._logger))

    def start(self) -> None:
        for resource in self._resources:
            resource.start()

    def stop(self) -> None:
        for resource in reversed(self._resources):
            resource.stop()


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()

    main = Main(logger=logger)
    main.start()

    _wait_for_exit()

    main.stop()


def _wait_for_exit() -> None:
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
