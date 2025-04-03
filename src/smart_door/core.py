from dataclasses import dataclass
from typing import Literal
from enum import Enum, auto
from datetime import datetime
from src.image_classifier.classification import Classification

#
#
#


class ConnectionState(Enum):
    Connecting = auto()
    Connected = auto()


@dataclass
class ModelConnecting:
    type: Literal["connecting"]
    camera: ConnectionState
    door: ConnectionState


#
#
#


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


#
#
#

Model = ModelConnecting | ModelReady


#
#
#
#
#


@dataclass
class MsgTick:
    type: Literal["tick"]
