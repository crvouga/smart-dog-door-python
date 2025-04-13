from logging import Logger
from src.device_camera.impl_fake import FakeDeviceCamera
from src.device_camera.interface import DeviceCamera
from src.image_classifier.impl_yolo import YoloImageClassifier, YoloModelSize
from src.smart_door.core import (
    MsgCameraEvent,
    MsgDoorEvent,
    MsgDoorEvent,
    ModelReady,
    transition,
    init,
)
from src.device_camera.event import EventCameraConnected
from src.device_door.event import EventDoorConnected
from src.smart_door.core.effect import Effect
from src.smart_door.core.model import Model
from src.smart_door.core.msg import Msg


class BaseFixture:
    def __init__(self) -> None:
        self.logger = Logger("test")
        self.device_camera: DeviceCamera = FakeDeviceCamera(logger=self.logger)
        self.image_classifier = YoloImageClassifier(model_size=YoloModelSize.NANO)

    def init(self) -> tuple[Model, list[Effect]]:
        return init()

    def transition(self, model: Model, msg: Msg) -> tuple[Model, list[Effect]]:
        return transition(model=model, msg=msg)

    def transition_to_ready_state(
        self, model: Model
    ) -> tuple[ModelReady, list[Effect]]:
        model, _ = transition(
            model=model,
            msg=MsgCameraEvent(camera_event=EventCameraConnected()),
        )

        model, effects = transition(
            model=model,
            msg=MsgDoorEvent(door_event=EventDoorConnected()),
        )

        assert isinstance(model, ModelReady)

        return model, effects
