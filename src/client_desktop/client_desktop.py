from src.client_desktop.gui.gui import Gui
from src.library.life_cycle import LifeCycle
from src.smart_door.smart_door import SmartDoor
from src.device_camera.interface import DeviceCamera
from logging import Logger


class DesktopClient(LifeCycle):
    _logger: Logger
    _gui: Gui

    def __init__(
        self, logger: Logger, smart_door: SmartDoor, device_camera: DeviceCamera
    ) -> None:
        self._logger = logger.getChild("client_desktop")

        self._gui = Gui(
            logger=self._logger,
            smart_door=smart_door,
            device_camera=device_camera,
        )

    def start(self) -> None:
        self._logger.info("Starting")
        self._gui.start()
        self._logger.info("Started")

    def stop(self) -> None:
        self._logger.info("Stopping")
        self._gui.stop()
        self._logger.info("Stopped")
