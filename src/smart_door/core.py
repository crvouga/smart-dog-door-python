from dataclasses import dataclass
from typing import Literal, Union
from enum import Enum, auto
from datetime import datetime
from src.image_classifier.classification import Classification
from src.image.image import Image
from src.device_camera.event import EventDeviceCamera
from src.device_door.event import EventDeviceDoor
from src.library.result import Result


class ConnectionState(Enum):
    Connecting = auto()
    Connected = auto()


@dataclass
class ModelConnecting:
    camera: ConnectionState
    door: ConnectionState
    type: Literal["connecting"]


class CameraState(Enum):
    Idle = auto()
    Capturing = auto()
    Classifying = auto()


@dataclass
class ModelCamera:
    state: CameraState
    state_start_time: datetime
    latest_classification: list[list[Classification]]


class DoorState(Enum):
    Closed = auto()
    WillClose = auto()
    Open = auto()
    WillOpen = auto()


@dataclass
class ModelDoor:
    state: DoorState
    state_start_time: datetime


@dataclass
class ModelReady:
    camera: ModelCamera
    door: ModelDoor
    type: Literal["ready"]


Model = Union[ModelConnecting, ModelReady]


@dataclass
class MsgTick:
    type: Literal["tick"]
    time: datetime


@dataclass
class MsgCameraEvent:
    type: Literal["camera_event"]
    event: EventDeviceCamera


@dataclass
class MsgDoorEvent:
    type: Literal["door_event"]
    event: EventDeviceDoor


@dataclass
class MsgDoorCloseDone:
    type: Literal["door_close_done"]
    result: Result[None, Exception]


@dataclass
class MsgDoorOpenDone:
    type: Literal["door_open_done"]
    result: Result[None, Exception]


@dataclass
class MsgFramesCaptureDone:
    type: Literal["frames_capture_done"]
    result: Result[list[Image], Exception]


@dataclass
class MsgFramesClassifyDone:
    type: Literal["frames_classify_done"]
    result: Result[list[list[Classification]], Exception]


Msg = Union[
    MsgTick,
    MsgCameraEvent,
    MsgDoorEvent,
    MsgDoorCloseDone,
    MsgDoorOpenDone,
    MsgFramesCaptureDone,
    MsgFramesClassifyDone,
]


@dataclass
class EffectOpenDoor:
    type: Literal["open_door"]


@dataclass
class EffectCloseDoor:
    type: Literal["close_door"]


@dataclass
class EffectCaptureFrames:
    type: Literal["capture_frames"]


@dataclass
class EffectClassifyFrames:
    type: Literal["classify_frames"]
    frames: list[Image]


@dataclass
class EffectSubscribeCamera:
    type: Literal["subscribe_camera"]


@dataclass
class EffectSubscribeDoor:
    type: Literal["subscribe_door"]


@dataclass
class EffectSubscribeTick:
    type: Literal["subscribe_tick"]


Effect = Union[
    EffectOpenDoor,
    EffectCloseDoor,
    EffectCaptureFrames,
    EffectClassifyFrames,
    EffectSubscribeCamera,
    EffectSubscribeDoor,
    EffectSubscribeTick,
]


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
    elif isinstance(model, ModelReady) and model.type == "ready":
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

    if is_ready:
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
    return model_new, []


def _transition_connecting_door(
    connection_state: ConnectionState, msg: Msg
) -> ConnectionState:
    if not isinstance(msg, MsgDoorEvent):
        return connection_state

    if isinstance(msg.event, EventDeviceDoor.Connected):
        return ConnectionState.Connected

    if isinstance(msg.event, EventDeviceDoor.Disconnected):
        return ConnectionState.Connecting

    return connection_state


def _transition_connecting_camera(
    connection_state: ConnectionState, msg: Msg
) -> ConnectionState:
    if not isinstance(msg, MsgCameraEvent):
        return connection_state

    if isinstance(msg.event, EventDeviceCamera.Connected):
        return ConnectionState.Connected

    if isinstance(msg.event, EventDeviceCamera.Disconnected):
        return ConnectionState.Connecting

    return connection_state


def _transition_ready(model: ModelReady, msg: Msg) -> tuple[Model, list[Effect]]:
    return model, []
