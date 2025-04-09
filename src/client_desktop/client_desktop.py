import logging
from src.client_desktop.gui.gui import Gui
from src.library.life_cycle import LifeCycle
from src.smart_door.smart_door import SmartDoor
from src.device_camera.interface import DeviceCamera
from src.device_camera.impl_indexed import IndexedDeviceCamera
from src.device_camera.impl_wyze_client import WyzeSdkCamera
from src.device_door.impl_fake import FakeDeviceDoor
from src.device_door.interface import DeviceDoor
from src.image_classifier.impl_yolo import YoloImageClassifier, YoloModelSize
from src.image_classifier.interface import ImageClassifier
from src.library.wyze_sdk.wyze_client import WyzeClient
from src.env import Env


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

        self._device_camera = self._initialize_camera(env)

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

    def _initialize_camera(self, env: Env) -> DeviceCamera:
        try:
            wyze_client = WyzeClient(
                logger=self._logger,
                email=env.wyze_email,
                password=env.wyze_password,
                key_id=env.wyze_key_id,
                api_key=env.wyze_api_key,
            )

            wyze_devices = wyze_client.list_devices()

            if wyze_devices:
                wyze_device = wyze_devices[0]
                return WyzeSdkCamera(
                    wyze_client=wyze_client,
                    logger=self._logger,
                    device_mac=wyze_device.mac,
                    device_model=wyze_device.model,
                )

            return IndexedDeviceCamera(logger=self._logger, device_ids=[0])
        except Exception as e:
            self._logger.warning(f"Failed to initialize Wyze camera: {e}")
            return IndexedDeviceCamera(logger=self._logger, device_ids=[0])

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
