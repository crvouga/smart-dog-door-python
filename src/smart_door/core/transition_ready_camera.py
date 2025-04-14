from .model import (
    ModelReady,
    ModelCamera,
    CameraState,
)
from .msg import (
    Msg,
    MsgImageCaptureDone,
    MsgImageClassifyDone,
    MsgTick,
)
from .effect import (
    Effect,
    EffectCaptureImage,
    EffectClassifyImages,
)


def transition_ready_camera(
    model: ModelReady, camera: ModelCamera, msg: Msg
) -> tuple[ModelCamera, list[Effect]]:
    effects_new: list[Effect] = []

    camera_new, effects = _transition_camera_idle_to_capturing(
        model=model, camera=camera, msg=msg
    )
    effects_new.extend(effects)

    camera_new, effects = _transition_camera_capturing_to_classifying(
        camera=camera_new, msg=msg
    )
    effects_new.extend(effects)

    camera_new, effects = _transition_camera_classifying_to_idle(
        camera=camera_new, msg=msg
    )
    effects_new.extend(effects)

    return camera_new, effects_new


def _transition_camera_idle_to_capturing(
    model: ModelReady, camera: ModelCamera, msg: Msg
) -> tuple[ModelCamera, list[Effect]]:
    if not isinstance(msg, MsgTick):
        return camera, []

    if camera.state != CameraState.Idle:
        return camera, []

    should_capture = (
        camera.state_start_time + model.config.minimal_rate_camera_process
        < msg.happened_at
    )

    if not should_capture:
        return camera, []

    return (
        ModelCamera(
            state=CameraState.Capturing,
            state_start_time=msg.happened_at,
            classification_runs=camera.classification_runs,
        ),
        [EffectCaptureImage()],
    )


def _transition_camera_capturing_to_classifying(
    camera: ModelCamera, msg: Msg
) -> tuple[ModelCamera, list[Effect]]:
    if not isinstance(msg, MsgImageCaptureDone):
        return camera, []

    if camera.state != CameraState.Capturing:
        return camera, []

    if not msg.images:
        camera_new = ModelCamera(
            state=CameraState.Idle,
            state_start_time=msg.happened_at,
            classification_runs=camera.classification_runs,
        )
        return camera_new, []

    camera_new = ModelCamera(
        state=CameraState.Classifying,
        state_start_time=msg.happened_at,
        classification_runs=camera.classification_runs,
    )

    return camera_new, [EffectClassifyImages(images=msg.images)]


def _transition_camera_classifying_to_idle(
    camera: ModelCamera, msg: Msg
) -> tuple[ModelCamera, list[Effect]]:
    if not isinstance(msg, MsgImageClassifyDone):
        return camera, []

    if camera.state != CameraState.Classifying:
        return camera, []

    classification_runs_new = list(camera.classification_runs)
    classification_runs_new.append(msg.classification_run)

    camera_new = ModelCamera(
        state=CameraState.Idle,
        state_start_time=msg.happened_at,
        classification_runs=classification_runs_new,
    )

    return camera_new, []
