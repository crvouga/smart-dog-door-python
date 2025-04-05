from src.client_desktop.gui.gui import Gui
from src.device_camera.impl_indexed import IndexedDeviceCamera
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
    _gui: Gui
    _resources: list[LifeCycle]

    def __init__(self, logger: Logger) -> None:
        self._logger = logger.getChild("client_desktop")

        self._image_classifier = YoloImageClassifier(
            model_size=YoloModelSize.EXTRA_LARGE
        )

        self._device_door = FakeDeviceDoor(logger=self._logger)

        self._device_camera: DeviceCamera = IndexedDeviceCamera(
            logger=self._logger,
        )

        self._smart_door = SmartDoor(
            image_classifier=self._image_classifier,
            device_camera=self._device_camera,
            device_door=self._device_door,
            logger=self._logger,
        )

        self._gui = Gui(
            logger=self._logger,
            device_camera=self._device_camera,
            smart_door=self._smart_door,
        )

    def start(self) -> None:
        self._logger.info("Starting")
        self._device_door.start()
        self._device_camera.start()
        self._smart_door.start()
        self._gui.start()
        self._logger.info("Started")

    def stop(self) -> None:
        self._logger.info("Stopping")
        self._gui.stop()
        self._smart_door.stop()
        self._device_camera.stop()
        self._device_door.stop()
        self._logger.info("Stopped")
