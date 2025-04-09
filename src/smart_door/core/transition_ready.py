from src.device_camera.event import EventCameraDisconnected
from src.device_door.event import EventDoorDisconnected
from src.smart_door.core.transition_ready_door.transition_ready_door import (
    transition_ready_door,
)
from .model import (
    Model,
    ModelConnecting,
    ModelReady,
    ConnectionState,
)
from .msg import (
    Msg,
    MsgCameraEvent,
    MsgDoorEvent,
)
from .effect import (
    Effect,
)
from .transition_ready_camera import transition_ready_camera


def transition_ready(model: ModelReady, msg: Msg) -> tuple[Model, list[Effect]]:
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

    camera, effects = transition_ready_camera(model=model, camera=model.camera, msg=msg)
    effects_new.extend(effects)

    door, effects = transition_ready_door(model=model, door=model.door, msg=msg)
    effects_new.extend(effects)

    model_new = ModelReady(
        camera=camera,
        door=door,
    )

    return model_new, effects_new
