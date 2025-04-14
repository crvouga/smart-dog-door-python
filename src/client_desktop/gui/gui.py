from logging import Logger
from PySide6.QtWidgets import (  # type: ignore
    QApplication,
)
import sys
import signal  # Import the signal module
from src.device_camera.interface import DeviceCamera
from src.smart_door.smart_door import SmartDoor
from .window_main import WindowMain
from .window_debug import WindowDebug
from src.library.life_cycle import LifeCycle


class Gui(LifeCycle):
    _logger: Logger
    _app: QApplication
    _window: WindowMain
    _debug_window: WindowDebug

    def __init__(
        self, logger: Logger, device_camera: DeviceCamera, smart_door: SmartDoor
    ):
        self._logger = logger.getChild("gui")
        self._device_camera = device_camera
        self._smart_door = smart_door
        self._init_app()
        self._init_windows()
        self._init_signal_handler()

    def _init_app(self) -> None:
        app_instance = QApplication.instance()
        if not app_instance:
            self._app = QApplication(sys.argv)
        else:
            self._app = app_instance  # type: ignore

    def _init_windows(self) -> None:
        self._window = WindowMain(
            device_camera=self._device_camera, smart_door=self._smart_door
        )
        self._debug_window = WindowDebug(smart_door=self._smart_door)

        screen = self._app.primaryScreen().geometry()
        window_width = self._window.width()
        window_height = self._window.height()

        self._window.move(0, 0)

        self._debug_window.move(window_width, 0)

    def _init_signal_handler(self) -> None:
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, sig, frame):
        """Custom signal handler to quit the application gracefully."""
        self._logger.info("SIGINT received, initiating graceful shutdown.")
        # Stop all components in reverse order of initialization
        self._window.close()
        self._debug_window.close()
        self._smart_door.stop()
        self._device_camera.stop()
        # Give components a moment to clean up
        self._app.processEvents()
        # Now quit the application
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
