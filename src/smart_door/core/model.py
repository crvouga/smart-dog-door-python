from dataclasses import dataclass, field
from typing import Literal, Union
from enum import Enum, auto
from datetime import datetime
from src.image.image import Image
from src.image_classifier.classification import Classification
from src.smart_door.config import Config


@dataclass
class _ModelBase:
    type: str
    config: Config = field(default_factory=Config)


class ConnectionState(Enum):
    Connecting = auto()
    Connected = auto()

    def __repr__(self) -> str:
        return self.name


@dataclass
class ModelConnecting(_ModelBase):
    camera: ConnectionState = field(default=ConnectionState.Connecting)
    door: ConnectionState = field(default=ConnectionState.Connecting)
    type: Literal["connecting"] = "connecting"


class CameraState(Enum):
    Idle = auto()
    Capturing = auto()
    Classifying = auto()

    def __repr__(self) -> str:
        return self.name


@dataclass
class ClassificationRun:
    classifications: list[Classification] = field(default_factory=list)
    images: list[Image] = field(default_factory=list)
    finished_at: datetime = field(default_factory=datetime.now)


@dataclass
class ModelCamera:
    state: CameraState = field(default=CameraState.Idle)
    state_start_time: datetime = field(default_factory=datetime.now)
    classification_runs: list[ClassificationRun] = field(default_factory=list)


class DoorState(Enum):
    Closed = auto()
    WillClose = auto()
    Opened = auto()
    WillOpen = auto()

    def __repr__(self) -> str:
        return self.name


@dataclass
class ModelDoor:
    state: DoorState = field(default=DoorState.Closed)
    state_start_time: datetime = field(default_factory=datetime.now)


@dataclass
class ModelReady(_ModelBase):
    camera: ModelCamera = field(default_factory=ModelCamera)
    door: ModelDoor = field(default_factory=ModelDoor)
    type: Literal["ready"] = "ready"


Model = Union[ModelConnecting, ModelReady]


def is_camera_connected(model: Model) -> bool:
    if isinstance(model, ModelConnecting):
        return model.camera == ConnectionState.Connected
    return True


def to_latest_classifications(model: Model) -> list[Classification]:
    if isinstance(model, ModelReady):
        classifications: list[Classification] = [
            classification
            for classification_run in model.camera.classification_runs
            for classification in classification_run.classifications
        ]
        return classifications
    return []
