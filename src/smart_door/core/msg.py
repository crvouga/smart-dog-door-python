from dataclasses import dataclass, field
from typing import Literal, Optional, Union
from datetime import datetime
from src.image_classifier.classification import Classification
from src.image.image import Image
from src.device_camera.event import EventCamera
from src.device_door.event import EventDoor


@dataclass
class _MsgBase:
    happened_at: datetime = field(default_factory=datetime.now)


@dataclass
class MsgTick(_MsgBase):
    type: Literal["tick"] = "tick"


@dataclass
class MsgCameraEvent(_MsgBase):
    camera_event: Optional[EventCamera] = None
    type: Literal["camera_event"] = "camera_event"


@dataclass
class MsgDoorEvent(_MsgBase):
    door_event: Optional[EventDoor] = None
    type: Literal["door_event"] = "door_event"


@dataclass
class MsgDoorCloseDone(_MsgBase):
    type: Literal["door_close_done"] = "door_close_done"


@dataclass
class MsgDoorOpenDone(_MsgBase):
    type: Literal["door_open_done"] = "door_open_done"


@dataclass
class MsgImageCaptureDone(_MsgBase):
    images: list[Image] = field(default_factory=list)
    type: Literal["image_capture_done"] = "image_capture_done"


@dataclass
class MsgImageClassifyDone(_MsgBase):
    classifications: list[Classification] = field(default_factory=list)
    type: Literal["image_classify_done"] = "image_classify_done"


Msg = Union[
    MsgTick,
    MsgCameraEvent,
    MsgDoorEvent,
    MsgDoorCloseDone,
    MsgDoorOpenDone,
    MsgImageCaptureDone,
    MsgImageClassifyDone,
]
