from logging import Logger
from PySide6.QtWidgets import (  # type: ignore
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
)
from PySide6.QtCore import Qt  # type: ignore
import sys
from abc import ABCMeta

from src.library.life_cycle import LifeCycle


# Resolve metaclass conflict between QMainWindow and LifeCycle (ABC)
qt_meta = type(QMainWindow)


class CombinedMeta(qt_meta, ABCMeta):
    pass


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Classifier")
        self.setMinimumSize(400, 300)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Add title label
        title_label = QLabel("Image Classifier")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        layout.addWidget(title_label)

        # Add classify button
        classify_button = QPushButton("Classify Images")
        classify_button.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """
        )
        layout.addWidget(classify_button)

        # Add result label
        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet("font-size: 16px; margin: 20px;")
        layout.addWidget(self.result_label)

        # Connect button click
        classify_button.clicked.connect(self.on_classify_clicked)

    def on_classify_clicked(self):
        self.result_label.setText("Classification in progress...")


class Gui(LifeCycle, metaclass=CombinedMeta):
    _logger: Logger
    _app: QApplication
    _window: MainWindow

    def __init__(self, logger: Logger):
        super().__init__()
        self._logger = logger.getChild("gui")
        self._app = QApplication(sys.argv)
        self._window = MainWindow()

    def start(self) -> None:
        self._logger.info("Starting GUI")
        self._window.show()
        self._app.exec()
        self._logger.info("GUI started")

    def stop(self) -> None:
        self._logger.info("Stopping GUI")
        self._window.close()
        self._logger.info("GUI stopped")
