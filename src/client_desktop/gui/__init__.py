from logging import Logger
from PySide6.QtWidgets import (  # type: ignore
    QApplication,
    QMainWindow,
)
import sys
from abc import ABCMeta
from .main_window import MainWindow
from src.library.life_cycle import LifeCycle


qt_meta = type(QMainWindow)


class Meta(qt_meta, ABCMeta):
    pass


class Gui(LifeCycle, metaclass=Meta):
    _logger: Logger
    _app: QApplication
    _window: MainWindow

    def __init__(self, logger: Logger):
        super().__init__()
        self._logger = logger.getChild("gui")
        self._app = QApplication(sys.argv)
        self._window = MainWindow()

    def start(self) -> None:
        self._logger.info("Starting")
        self._window.show()
        self._app.exec()
        self._logger.info("Started")

    def stop(self) -> None:
        self._logger.info("Stopping")
        self._window.close()
        self._logger.info("Stopped")
