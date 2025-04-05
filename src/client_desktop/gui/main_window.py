from PySide6.QtWidgets import (  # type: ignore
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QHBoxLayout,
)
from PySide6.QtCore import Qt  # type: ignore
from .camera_feed_widget import CameraFeedWidget
from src.device_camera.interface import DeviceCamera


class MainWindow(QMainWindow):
    def __init__(self, device_camera: DeviceCamera):
        super().__init__()

        self.setWindowTitle("Image Classifier")
        ASPECT_RATIO_H_W = 9 / 16
        WIDTH = 1000
        HEIGHT = WIDTH * ASPECT_RATIO_H_W
        self.setMinimumSize(WIDTH, HEIGHT)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Add title label
        title_label = QLabel("Image Classifier")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        main_layout.addWidget(title_label)

        # Create camera feed container with horizontal layout for centering
        camera_container = QWidget()
        camera_layout = QHBoxLayout(camera_container)
        camera_layout.setAlignment(Qt.AlignCenter)

        # Add camera feed widget
        self.camera_feed = CameraFeedWidget(device_camera=device_camera)
        camera_layout.addWidget(self.camera_feed)
        main_layout.addWidget(camera_container)

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
        main_layout.addWidget(classify_button)

        # Add result label
        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet("font-size: 16px; margin: 20px;")
        main_layout.addWidget(self.result_label)

        # Connect button click
        classify_button.clicked.connect(self.on_classify_clicked)

    def on_classify_clicked(self):
        self.result_label.setText("Classification in progress...")
