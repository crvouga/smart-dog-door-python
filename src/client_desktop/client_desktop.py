import logging
from typing import Optional
from src.client_desktop.gui.gui import Gui
from src.device_camera.interface import DeviceCamera
from src.library.life_cycle import LifeCycle
from src.smart_door.smart_door import SmartDoor
from src.device_door.impl_fake import FakeDeviceDoor
from src.device_door.interface import DeviceDoor
from src.image_classifier.impl_yolo import YoloImageClassifier, YoloModelSize
from src.image_classifier.interface import ImageClassifier
from src.env import Env
from src.device_camera.factory import create_camera


class DesktopClient(LifeCycle):
    _logger: logging.Logger
    _gui: Gui
    _image_classifier: ImageClassifier
    _device_door: DeviceDoor
    _device_camera: DeviceCamera
    _smart_door: SmartDoor

    def __init__(self, env: Env, logger: logging.Logger) -> None:
        self._logger = logger.getChild("client_desktop")

        self._image_classifier = YoloImageClassifier(
            model_size=YoloModelSize.EXTRA_LARGE
        )

        self._device_door = FakeDeviceDoor(logger=self._logger)

        self._device_camera = create_camera(env=env, logger=self._logger)

        self._smart_door = SmartDoor(
            image_classifier=self._image_classifier,
            device_camera=self._device_camera,
            device_door=self._device_door,
            logger=self._logger,
        )

        self._gui = Gui(
            logger=self._logger,
            smart_door=self._smart_door,
            device_camera=self._device_camera,
        )

    def start(self) -> None:
        self._logger.info("Starting")
        self._device_camera.start()
        self._device_door.start()
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
