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
from .msg import Msg, MsgCameraEvent, MsgDoorEvent
from .effect import Effect


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
    return model, []
