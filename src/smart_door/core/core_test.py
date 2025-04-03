from src.smart_door.core import (
    init,
    transition,
    ConnectionState,
    CameraState,
    DoorState,
    EffectSubscribeCamera,
    EffectSubscribeDoor,
    EffectSubscribeTick,
    MsgCameraEvent,
    MsgDoorEvent,
    MsgDoorEvent,
    ModelReady,
)
from src.device_camera.event import EventCameraConnected
from src.device_door.event import EventDoorConnected


def test_init() -> None:
    model, effects = init()

    assert model.type == "connecting"
    assert model.camera == ConnectionState.Connecting
    assert model.door == ConnectionState.Connecting

    assert len(effects) == 3
    assert isinstance(effects[0], EffectSubscribeCamera)
    assert isinstance(effects[1], EffectSubscribeDoor)
    assert isinstance(effects[2], EffectSubscribeTick)


def test_transition_to_ready_state() -> None:
    model, _ = init()

    model, _ = transition(
        model=model,
        msg=MsgCameraEvent(event=EventCameraConnected()),
    )

    model, _ = transition(
        model=model,
        msg=MsgDoorEvent(event=EventDoorConnected()),
    )

    assert isinstance(model, ModelReady)
    assert model.camera.state == CameraState.Idle
    assert model.door.state == DoorState.Closed
