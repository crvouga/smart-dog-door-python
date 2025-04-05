from src.client_desktop.gui import Gui
from src.device_camera.impl_fake import FakeDeviceCamera
from src.device_door.impl_fake import FakeDeviceDoor
from src.image_classifier.impl_yolo import YoloImageClassifier, YoloModelSize
from src.library.life_cycle import LifeCycle
from src.smart_door.smart_door import SmartDoor
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
    _resources: list[LifeCycle]

    def __init__(self, logger: Logger) -> None:
        self._logger = logger.getChild("client_desktop")

        self._image_classifier = YoloImageClassifier(model_size=YoloModelSize.LARGE)

        self._device_door = FakeDeviceDoor(logger=self._logger)

        self._device_camera = FakeDeviceCamera(
            logger=self._logger,
        )

        self._gui = Gui(logger=self._logger)

        self._smart_door = SmartDoor(
            image_classifier=self._image_classifier,
            device_camera=self._device_camera,
            device_door=self._device_door,
            logger=self._logger,
        )

        self._resources = [
            self._smart_door,
            self._gui,
        ]

    def start(self) -> None:
        self._logger.info("Starting desktop client")
        for resource in self._resources:
            resource.start()
        self._logger.info("Desktop client started")

    def stop(self) -> None:
        self._logger.info("Stopping desktop client")
        for resource in reversed(self._resources):
            resource.stop()
        self._logger.info("Desktop client stopped")
