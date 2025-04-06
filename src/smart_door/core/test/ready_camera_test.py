from datetime import datetime, timedelta
from src.smart_door.core import (
    EffectCaptureImage,
    EffectClassifyImages,
    CameraState,
    ModelReady,
    MsgImageCaptureDone,
    MsgImageClassifyDone,
)
from src.smart_door.core.msg import MsgTick
from src.smart_door.core.test.fixture import BaseFixture


def test_transition_camera_to_capturing_state() -> None:
    f = BaseFixture()

    model, _ = f.init()

    model, _ = f.transition_to_ready_state(model=model)

    model, effects = f.transition(
        model=model,
        msg=MsgTick(
            happened_at=datetime.now() + model.config.minimal_rate_camera_process
        ),
    )

    assert isinstance(model, ModelReady)
    assert len(effects) == 1
    assert isinstance(effects[0], EffectCaptureImage)
    assert model.camera.state == CameraState.Capturing


def test_do_not_transition_to_capturing_state_if_not_enough_time_has_passed() -> None:
    f = BaseFixture()

    model, _ = f.init()

    model, _ = f.transition_to_ready_state(model=model)

    model, _ = f.transition(
        model=model,
        msg=MsgTick(
            happened_at=datetime.now()
            + model.config.minimal_rate_camera_process
            - timedelta(seconds=1)
        ),
    )

    assert isinstance(model, ModelReady)
    assert model.camera.state == CameraState.Idle


def test_transition_to_classifying_state_after_capturing_image() -> None:
    f = BaseFixture()

    model, _ = f.init()

    model, _ = f.transition_to_ready_state(model=model)

    model, _ = f.transition(
        model=model,
        msg=MsgTick(
            happened_at=datetime.now() + model.config.minimal_rate_camera_process
        ),
    )

    assert isinstance(model, ModelReady)
    assert model.camera.state == CameraState.Capturing

    model, effects = f.transition(
        model=model, msg=MsgImageCaptureDone(images=f.device_camera.capture())
    )

    assert len(effects) == 1
    assert isinstance(effects[0], EffectClassifyImages)

    assert isinstance(model, ModelReady)
    assert model.camera.state == CameraState.Classifying


def test_transition_to_idle_state_after_classifying_image() -> None:
    f = BaseFixture()

    model, _ = f.init()

    model, _ = f.transition_to_ready_state(model=model)

    model, _ = f.transition(
        model=model,
        msg=MsgTick(
            happened_at=datetime.now() + model.config.minimal_rate_camera_process
        ),
    )

    images = f.device_camera.capture()

    model, _ = f.transition(model=model, msg=MsgImageCaptureDone(images=images))

    model, _ = f.transition(
        model=model,
        msg=MsgImageClassifyDone(
            classifications=f.image_classifier.classify(images=images)
        ),
    )

    assert isinstance(model, ModelReady)
    assert model.camera.state == CameraState.Idle
