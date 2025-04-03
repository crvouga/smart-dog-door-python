from dataclasses import dataclass
from typing import Literal, Union
from datetime import datetime
from src.image_classifier.classification import Classification
from src.image.image import Image
from src.device_camera.event import EventCamera
from src.device_door.event import EventDoor
from src.library.result import Result


@dataclass
class MsgTick:
    time: datetime
    type: Literal["tick"] = "tick"


@dataclass
class MsgCameraEvent:
    event: EventCamera
    type: Literal["camera_event"] = "camera_event"


@dataclass
class MsgDoorEvent:
    event: EventDoor
    type: Literal["door_event"] = "door_event"


@dataclass
class MsgDoorCloseDone:
    result: Result[None, Exception]
    type: Literal["door_close_done"] = "door_close_done"


@dataclass
class MsgDoorOpenDone:
    result: Result[None, Exception]
    type: Literal["door_open_done"] = "door_open_done"


@dataclass
class MsgFramesCaptureDone:
    result: Result[list[Image], Exception]
    type: Literal["frames_capture_done"] = "frames_capture_done"


@dataclass
class MsgFramesClassifyDone:
    result: Result[list[Classification], Exception]
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
