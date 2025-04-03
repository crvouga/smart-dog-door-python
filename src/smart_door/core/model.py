from dataclasses import dataclass
from typing import Literal, Union
from enum import Enum, auto
from datetime import datetime
from src.image_classifier.classification import Classification


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
