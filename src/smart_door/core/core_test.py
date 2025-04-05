from datetime import datetime, timedelta
from src.smart_door.config import Config
from src.smart_door.core import (
    Transition,
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
from src.smart_door.core.model import Model
from src.smart_door.core.msg import MsgTick


def test_init() -> None:
    t = Transition(config=Config())

    model, effects = t.init()

    assert model.type == "connecting"
    assert model.camera == ConnectionState.Connecting
    assert model.door == ConnectionState.Connecting

    assert len(effects) == 3
    assert isinstance(effects[0], EffectSubscribeCamera)
    assert isinstance(effects[1], EffectSubscribeDoor)
    assert isinstance(effects[2], EffectSubscribeTick)


def _transition_to_ready_state(t: Transition, model: Model) -> ModelReady:

    model, _ = t.transition(
        model=model,
        msg=MsgCameraEvent(camera_event=EventCameraConnected()),
    )

    model, _ = t.transition(
        model=model,
        msg=MsgDoorEvent(door_event=EventDoorConnected()),
    )

    assert isinstance(model, ModelReady)

    return model


def test_transition_to_ready_state() -> None:
    t = Transition(config=Config())

    model, _ = t.init()

    model = _transition_to_ready_state(t=t, model=model)

    assert isinstance(model, ModelReady)
    assert model.camera.state == CameraState.Idle
    assert model.door.state == DoorState.Closed


def test_transition_camera_to_capturing_state() -> None:
    config = Config()

    t = Transition(config=config)

    model, _ = t.init()

    model = _transition_to_ready_state(t=t, model=model)

    model, _ = t.transition(
        model=model,
        msg=MsgTick(happened_at=datetime.now() + config.minimal_rate_camera_process),
    )

    assert isinstance(model, ModelReady)
    assert model.camera.state == CameraState.Capturing


def test_do_not_transition_to_capturing_state_if_not_enough_time_has_passed() -> None:
    config = Config()

    t = Transition(config=config)

    model, _ = t.init()

    model = _transition_to_ready_state(t=t, model=model)

    model, _ = t.transition(
        model=model,
        msg=MsgTick(
            happened_at=datetime.now()
            + config.minimal_rate_camera_process
            - timedelta(seconds=1)
        ),
    )

    assert isinstance(model, ModelReady)
    assert model.camera.state == CameraState.Idle
