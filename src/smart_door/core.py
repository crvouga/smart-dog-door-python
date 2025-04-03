from dataclasses import dataclass
from typing import Literal, Union
from enum import Enum, auto
from datetime import datetime
from src.image_classifier.classification import Classification
from src.image.image import Image
from src.device_camera.interface import DeviceCameraEvent


class ConnectionState(Enum):
    Connecting = auto()
    Connected = auto()


@dataclass
class ModelConnecting:
    type: Literal["connecting"]
    camera: ConnectionState
    door: ConnectionState


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
    type: Literal["ready"]
    camera: ModelCamera
    door: ModelDoor


Model = Union[ModelConnecting, ModelReady]


@dataclass
class MsgTick:
    type: Literal["tick"]
    time: datetime


@dataclass
class MsgCameraEvent:
    type: Literal["camera_event"]
    event: DeviceCameraEvent


@dataclass
class MsgDoorEvent:
    type: Literal["door_event"]
    event: DeviceDoorEvent


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
