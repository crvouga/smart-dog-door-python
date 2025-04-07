from src.client_console.client_console import ConsoleClient
from src.client_desktop.client_desktop import DesktopClient
import logging
from src.device_camera.impl_indexed import IndexedDeviceCamera
from src.device_camera.interface import DeviceCamera
from src.device_door.impl_fake import FakeDeviceDoor
from src.device_door.interface import DeviceDoor
from src.image_classifier.impl_yolo import YoloImageClassifier, YoloModelSize
from src.image_classifier.interface import ImageClassifier
from src.library.life_cycle import LifeCycle
from src.smart_door.smart_door import SmartDoor
from src.env import load_env

logging.basicConfig(level=logging.INFO)


class App(LifeCycle):
    _logger: logging.Logger
    _client: LifeCycle
    _image_classifier: ImageClassifier
    _device_door: DeviceDoor
    _device_camera: DeviceCamera
    _smart_door: SmartDoor

    def __init__(
        self,
    ) -> None:
        self._logger = logging.getLogger("app")

        env = load_env()

        self._image_classifier = YoloImageClassifier(
            model_size=YoloModelSize.EXTRA_LARGE
        )

        self._device_door = FakeDeviceDoor(logger=self._logger)

        self._device_camera = IndexedDeviceCamera(logger=self._logger, device_ids=[0])

        self._smart_door = SmartDoor(
            image_classifier=self._image_classifier,
            device_camera=self._device_camera,
            device_door=self._device_door,
            logger=self._logger,
        )

        self._client = DesktopClient(
            logger=self._logger,
            smart_door=self._smart_door,
            device_camera=self._device_camera,
        )

    def start(self) -> None:
        self._logger.info("Starting")
        self._device_camera.start()
        self._device_door.start()
        self._smart_door.start()
        self._client.start()
        self._logger.info("Started")

    def stop(self) -> None:
        self._logger.info("Stopping")
        self._client.stop()
        self._smart_door.stop()
        self._device_camera.stop()
        self._device_door.stop()
        self._logger.info("Stopped")
