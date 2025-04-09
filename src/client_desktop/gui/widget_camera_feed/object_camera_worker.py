from PySide6.QtCore import QTimer, Signal, QObject  # type: ignore
from PySide6.QtGui import QImage  # type: ignore
from src.device_camera.interface import DeviceCamera


class ObjectCameraWorker(QObject):
    image_ready = Signal(QImage)

    def __init__(self, device_camera: DeviceCamera, fps: int):
        super().__init__()
        self._device_camera = device_camera
        self._running = True
        self._timer = QTimer()
        self._timer.timeout.connect(self._capture_frame)
        interval = int(1000 / fps)
        self._timer.start(interval)

    def _capture_frame(self):
        if not self._running:
            return

        image = self._device_camera.capture()

        if not image:
            return

        image = image[0]
        image = image.np_array
        height, width, _ = image.shape
        bytes_per_line = 3 * width
        q_image = QImage(
            image.data, width, height, bytes_per_line, QImage.Format_RGB888
        )
        self.image_ready.emit(q_image)

    def process(self):
        pass

    def stop(self):
        self._running = False
        self._timer.stop()
