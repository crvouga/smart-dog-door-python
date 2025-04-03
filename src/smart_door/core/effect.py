from dataclasses import dataclass
from typing import Literal, Union
from src.image.image import Image


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
