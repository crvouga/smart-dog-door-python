from src.library.life_cycle import LifeCycle
from src.smart_door.smart_door import SmartDoor
from logging import Logger


class ConsoleClient(LifeCycle):
    _logger: Logger

    def __init__(self, logger: Logger, smart_door: SmartDoor) -> None:
        self._logger = logger.getChild("client_console")

    def start(self) -> None:
        self._logger.info("Starting")
        pass
        self._logger.info("Started")

    def stop(self) -> None:
        self._logger.info("Stopping")
        pass
        self._logger.info("Stopped")
