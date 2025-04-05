from logging import Logger
from PySide6.QtWidgets import (  # type: ignore
    QApplication,
)
import sys
import signal  # Import the signal module
from src.device_camera.interface import DeviceCamera
from src.smart_door.smart_door import SmartDoor
from .main_window import MainWindow
from .debug_window import DebugWindow
from src.library.life_cycle import LifeCycle


class Gui(LifeCycle):
    _logger: Logger
    _app: QApplication
    _window: MainWindow
    _debug_window: DebugWindow

    def __init__(
        self, logger: Logger, device_camera: DeviceCamera, smart_door: SmartDoor
    ):
        self._logger = logger.getChild("gui")

        # Ensure QApplication exists (Singleton Pattern)
        app_instance = QApplication.instance()
        if not app_instance:
            self._app = QApplication(sys.argv)
        else:
            self._app = app_instance  # type: ignore

        self._window = MainWindow(device_camera=device_camera, smart_door=smart_door)
        self._debug_window = DebugWindow(smart_door=smart_door)

        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, sig, frame):
        """Custom signal handler to quit the application gracefully."""
        self._logger.info("SIGINT received, quitting application.")
        self._app.quit()

    def start(self) -> None:
        self._logger.info("Starting")
        self._window.show()
        self._debug_window.show()
        self._app.exec()
        self._logger.info("Started")

    def stop(self) -> None:
        self._logger.info("Stopping GUI")
        # Ensure stop is called from the main thread or via a queued connection
        # if stop might be triggered from another thread.
        self._window.close()
        self._debug_window.close()
        # self._app.quit() # Usually not needed here if signal handler works
        self._logger.info("GUI stopped")
