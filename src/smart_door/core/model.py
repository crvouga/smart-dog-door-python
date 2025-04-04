from dataclasses import dataclass
from typing import Literal, Union
from enum import Enum, auto
from datetime import datetime
from src.image_classifier.classification import Classification


class ConnectionState(Enum):
    Connecting = auto()
    Connected = auto()

    def __repr__(self) -> str:
        return self.name


@dataclass
class ModelConnecting:
    camera: ConnectionState
    door: ConnectionState
    type: Literal["connecting"]


class CameraState(Enum):
    Idle = auto()
    Capturing = auto()
    Classifying = auto()

    def __repr__(self) -> str:
        return self.name


@dataclass
class ModelCamera:
    state: CameraState
    state_start_time: datetime
    latest_classification: list[Classification]


class DoorState(Enum):
    Closed = auto()
    WillClose = auto()
    Open = auto()
    WillOpen = auto()

    def __repr__(self) -> str:
        return self.name


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
