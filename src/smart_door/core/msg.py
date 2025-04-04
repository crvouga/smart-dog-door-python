from dataclasses import dataclass
from typing import Literal, Union
from datetime import datetime
from src.image_classifier.classification import Classification
from src.image.image import Image
from src.device_camera.event import EventCamera
from src.device_door.event import EventDoor


@dataclass
class MsgTick:
    now: datetime
    type: Literal["tick"] = "tick"


@dataclass
class MsgCameraEvent:
    camera_event: EventCamera
    type: Literal["camera_event"] = "camera_event"


@dataclass
class MsgDoorEvent:
    door_event: EventDoor
    type: Literal["door_event"] = "door_event"


@dataclass
class MsgDoorCloseDone:
    type: Literal["door_close_done"] = "door_close_done"


@dataclass
class MsgDoorOpenDone:
    type: Literal["door_open_done"] = "door_open_done"


@dataclass
class MsgFramesCaptureDone:
    images: list[Image]
    type: Literal["frames_capture_done"] = "frames_capture_done"


@dataclass
class MsgFramesClassifyDone:
    classifications: list[Classification]
    type: Literal["frames_classify_done"] = "frames_classify_done"


Msg = Union[
    MsgTick,
    MsgCameraEvent,
    MsgDoorEvent,
    MsgDoorCloseDone,
    MsgDoorOpenDone,
    MsgFramesCaptureDone,
    MsgFramesClassifyDone,
]
