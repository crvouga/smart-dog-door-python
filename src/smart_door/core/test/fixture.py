from src.smart_door.config import Config
from src.smart_door.core import (
    Transition,
    MsgCameraEvent,
    MsgDoorEvent,
    MsgDoorEvent,
    ModelReady,
)
from src.device_camera.event import EventCameraConnected
from src.device_door.event import EventDoorConnected
from src.smart_door.core.model import Model


class Fixture:
    def __init__(self) -> None:
        self.config = Config()
        self.t = Transition(config=self.config)

    def transition_to_ready_state(self, model: Model) -> ModelReady:
        model, _ = self.t.transition(
            model=model,
            msg=MsgCameraEvent(camera_event=EventCameraConnected()),
        )

        model, _ = self.t.transition(
            model=model,
            msg=MsgDoorEvent(door_event=EventDoorConnected()),
        )

        assert isinstance(model, ModelReady)

        return model
