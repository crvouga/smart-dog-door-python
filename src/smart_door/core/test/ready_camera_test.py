from datetime import datetime, timedelta
from src.smart_door.core import (
    EffectCaptureImage,
    CameraState,
    ModelReady,
)
from src.smart_door.core.msg import MsgTick
from src.smart_door.core.test.fixture import Fixture


def test_transition_camera_to_capturing_state() -> None:
    f = Fixture()

    model, _ = f.t.init()

    model = f.transition_to_ready_state(model=model)

    model, effects = f.t.transition(
        model=model,
        msg=MsgTick(happened_at=datetime.now() + f.config.minimal_rate_camera_process),
    )

    assert isinstance(model, ModelReady)
    assert len(effects) == 1
    assert isinstance(effects[0], EffectCaptureImage)
    assert model.camera.state == CameraState.Capturing


def test_do_not_transition_to_capturing_state_if_not_enough_time_has_passed() -> None:
    f = Fixture()

    model, _ = f.t.init()

    model = f.transition_to_ready_state(model=model)

    model, _ = f.t.transition(
        model=model,
        msg=MsgTick(
            happened_at=datetime.now()
            + f.config.minimal_rate_camera_process
            - timedelta(seconds=1)
        ),
    )

    assert isinstance(model, ModelReady)
    assert model.camera.state == CameraState.Idle
