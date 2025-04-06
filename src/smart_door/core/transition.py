from datetime import datetime
from src.device_camera.event import EventCameraConnected, EventCameraDisconnected
from src.device_door.event import EventDoorConnected, EventDoorDisconnected
from .model import (
    Model,
    ModelConnecting,
    ModelReady,
    ModelCamera,
    ModelDoor,
    ConnectionState,
    CameraState,
    DoorState,
)
from .msg import (
    Msg,
    MsgCameraEvent,
    MsgDoorEvent,
    MsgImageCaptureDone,
    MsgImageClassifyDone,
    MsgTick,
)
from .effect import (
    Effect,
    EffectCaptureImage,
    EffectClassifyImages,
    EffectSubscribeCamera,
    EffectSubscribeDoor,
    EffectSubscribeTick,
)


def init() -> tuple[Model, list[Effect]]:
    return (
        ModelConnecting(
            type="connecting",
            camera=ConnectionState.Connecting,
            door=ConnectionState.Connecting,
        ),
        [
            EffectSubscribeCamera(type="subscribe_camera"),
            EffectSubscribeDoor(type="subscribe_door"),
            EffectSubscribeTick(type="subscribe_tick"),
        ],
    )


def transition(model: Model, msg: Msg) -> tuple[Model, list[Effect]]:
    if isinstance(model, ModelConnecting) and model.type == "connecting":
        return _transition_connecting(model=model, msg=msg)

    if isinstance(model, ModelReady) and model.type == "ready":
        return _transition_ready(model=model, msg=msg)


def _transition_connecting(
    model: ModelConnecting, msg: Msg
) -> tuple[Model, list[Effect]]:
    model_new = ModelConnecting(
        type="connecting",
        camera=_transition_connecting_camera(model.camera, msg),
        door=_transition_connecting_door(model.door, msg),
    )

    is_ready = (
        model_new.camera == ConnectionState.Connected
        and model_new.door == ConnectionState.Connected
    )

    if not is_ready:
        return model_new, []

    return (
        ModelReady(
            type="ready",
            camera=ModelCamera(
                state=CameraState.Idle,
                state_start_time=datetime.now(),
                latest_classification=[],
            ),
            door=ModelDoor(
                state=DoorState.Closed,
                state_start_time=datetime.now(),
            ),
        ),
        [],
    )


def _transition_connecting_door(
    connection_state: ConnectionState, msg: Msg
) -> ConnectionState:
    if not isinstance(msg, MsgDoorEvent):
        return connection_state

    if isinstance(msg.door_event, EventDoorConnected):
        return ConnectionState.Connected

    if isinstance(msg.door_event, EventDoorDisconnected):
        return ConnectionState.Connecting

    return connection_state


def _transition_connecting_camera(
    connection_state: ConnectionState, msg: Msg
) -> ConnectionState:
    if not isinstance(msg, MsgCameraEvent):
        return connection_state

    if isinstance(msg.camera_event, EventCameraConnected):
        return ConnectionState.Connected

    if isinstance(msg.camera_event, EventCameraDisconnected):
        return ConnectionState.Connecting

    return connection_state


def _transition_ready(model: ModelReady, msg: Msg) -> tuple[Model, list[Effect]]:
    if isinstance(msg, MsgCameraEvent) and isinstance(
        msg.camera_event, EventCameraDisconnected
    ):
        return (
            ModelConnecting(
                type="connecting",
                camera=ConnectionState.Connecting,
                door=ConnectionState.Connected,
            ),
            [],
        )

    if isinstance(msg, MsgDoorEvent) and isinstance(
        msg.door_event, EventDoorDisconnected
    ):
        return (
            ModelConnecting(
                type="connecting",
                camera=ConnectionState.Connected,
                door=ConnectionState.Connecting,
            ),
            [],
        )

    return _transition_ready_main(model=model, msg=msg)


def _transition_ready_main(model: ModelReady, msg: Msg) -> tuple[Model, list[Effect]]:
    effects_new: list[Effect] = []

    camera, effects = _transition_ready_camera(
        model=model, camera=model.camera, msg=msg
    )
    effects_new.extend(effects)

    model_new = ModelReady(
        camera=camera,
        door=model.door,
    )

    return model_new, effects_new


def _transition_ready_camera(
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
            latest_classification=camera.latest_classification,
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

    camera_new = ModelCamera(
        state=CameraState.Classifying,
        state_start_time=msg.happened_at,
        latest_classification=camera.latest_classification,
    )

    return camera_new, [EffectClassifyImages(images=msg.images)]


def _transition_camera_classifying_to_idle(
    camera: ModelCamera, msg: Msg
) -> tuple[ModelCamera, list[Effect]]:
    if not isinstance(msg, MsgImageClassifyDone):
        return camera, []

    if camera.state != CameraState.Classifying:
        return camera, []

    camera_new = ModelCamera(
        state=CameraState.Idle,
        state_start_time=msg.happened_at,
        latest_classification=msg.classifications,
    )

    return camera_new, []
