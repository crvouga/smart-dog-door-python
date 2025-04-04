from src.image_classifier.build import BuildImageClassifier
from src.library.life_cycle import LifeCycle
from src.smart_door.smart_door import SmartDoor
from src.device_camera.build import BuildDeviceCamera
from src.device_door.build import BuildDeviceDoor
from src.image_classifier.interface import ImageClassifier
from src.device_camera.interface import DeviceCamera
from src.device_door.interface import DeviceDoor
from logging import Logger


class DesktopClient(LifeCycle):
    _logger: Logger
    _image_classifier: ImageClassifier
    _device_door: DeviceDoor
    _device_camera: DeviceCamera
    _smart_door: SmartDoor

    def __init__(self, logger: Logger) -> None:
        self._logger = logger.getChild("client_desktop")
        self._image_classifier = BuildImageClassifier.fake()
        self._device_door = BuildDeviceDoor.fake()
        self._device_camera = BuildDeviceCamera.fake()

        self._smart_door = SmartDoor(
            image_classifier=self._image_classifier,
            device_camera=self._device_camera,
            device_door=self._device_door,
            logger=self._logger,
        )

    def start(self) -> None:
        self._logger.info("Starting desktop client")
        self._smart_door.start()
        self._logger.info("Desktop client started")

    def stop(self) -> None:
        self._logger.info("Stopping desktop client")
        self._smart_door.stop()
        self._logger.info("Desktop client stopped")
