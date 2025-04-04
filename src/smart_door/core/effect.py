from dataclasses import dataclass
from typing import Literal, Union
from src.image.image import Image


@dataclass
class EffectOpenDoor:
    type: Literal["open_door"] = "open_door"


@dataclass
class EffectCloseDoor:
    type: Literal["close_door"] = "close_door"


@dataclass
class EffectCaptureFrames:
    type: Literal["capture_frames"] = "capture_frames"


@dataclass
class EffectClassifyImages:
    images: list[Image]
    type: Literal["classify_images"] = "classify_images"


@dataclass
class EffectSubscribeCamera:
    type: Literal["subscribe_camera"] = "subscribe_camera"


@dataclass
class EffectSubscribeDoor:
    type: Literal["subscribe_door"] = "subscribe_door"


@dataclass
class EffectSubscribeTick:
    type: Literal["subscribe_tick"] = "subscribe_tick"


Effect = Union[
    EffectOpenDoor,
    EffectCloseDoor,
    EffectCaptureFrames,
    EffectClassifyImages,
    EffectSubscribeCamera,
    EffectSubscribeDoor,
    EffectSubscribeTick,
]
