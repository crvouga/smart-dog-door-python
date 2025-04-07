from src.device_camera.event import EventCameraConnected, EventCameraDisconnected
from src.device_door.event import EventDoorConnected, EventDoorDisconnected
from src.smart_door.core.model import ConnectionState, ModelConnecting, ModelReady
from src.smart_door.core.msg import MsgCameraEvent, MsgDoorEvent
from src.smart_door.core.test.fixture import BaseFixture


class Fixture(BaseFixture):
    def __init__(self) -> None:
        super().__init__()
        self.model, _ = self.init()
        self.model, _ = self.transition_to_ready_state(model=self.model)


def test_transition_to_ready_state() -> None:
    f = Fixture()

    model, _ = f.init()

    model, _ = f.transition(
        model=model,
        msg=MsgCameraEvent(camera_event=EventCameraConnected()),
    )

    model, _ = f.transition(
        model=model,
        msg=MsgDoorEvent(door_event=EventDoorConnected()),
    )

    assert isinstance(model, ModelReady)


def test_transition_to_connecting_state_when_camera_disconnected() -> None:
    f = Fixture()

    model, _ = f.transition(
        model=f.model,
        msg=MsgCameraEvent(camera_event=EventCameraDisconnected()),
    )

    assert isinstance(model, ModelConnecting)
    assert model.camera == ConnectionState.Connecting
    assert model.door == ConnectionState.Connected


def test_transition_to_connecting_state_when_door_disconnected() -> None:
    f = Fixture()

    model, _ = f.transition(
        model=f.model,
        msg=MsgDoorEvent(door_event=EventDoorDisconnected()),
    )

    assert isinstance(model, ModelConnecting)
    assert model.camera == ConnectionState.Connected
    assert model.door == ConnectionState.Connecting
