import time
from datetime import datetime
from .core import (
    Effect,
    Msg,
    EffectCaptureFrames,
    EffectClassifyFrames,
    EffectSubscribeCamera,
    EffectSubscribeDoor,
    EffectSubscribeTick,
    EffectOpenDoor,
    EffectCloseDoor,
    MsgFramesCaptureDone,
    MsgFramesClassifyDone,
    MsgDoorOpenDone,
    MsgDoorCloseDone,
    MsgTick,
    MsgDoorEvent,
    MsgCameraEvent,
)
from src.library.result import attempt, Ok, Err
import queue
from .deps import Deps
from src.library.time import ticks


def interpret_effect(deps: Deps, effect: Effect, msg_queue: queue.Queue[Msg]) -> None:
    if isinstance(effect, EffectSubscribeCamera):
        sub = deps.device_camera.events()
        sub.sub(lambda event: msg_queue.put(MsgCameraEvent(event=event)))

    if isinstance(effect, EffectSubscribeDoor):
        sub = deps.device_door.events()
        sub.sub(lambda event: msg_queue.put(MsgDoorEvent(event=event)))

    if isinstance(effect, EffectSubscribeTick):
        sub = ticks(interval_seconds=1)
        sub.sub(lambda dt: msg_queue.put(MsgTick(time=dt)))

    if isinstance(effect, EffectCaptureFrames):
        result = attempt(lambda: deps.device_camera.capture())
        msg_queue.put(MsgFramesCaptureDone(result=result))

    if isinstance(effect, EffectClassifyFrames):
        result = attempt(lambda: deps.image_classifier.classify(effect.frames))
        msg_queue.put(MsgFramesClassifyDone(result=result))

    if isinstance(effect, EffectOpenDoor):
        result = attempt(lambda: deps.device_door.open())
        msg_queue.put(MsgDoorOpenDone(result=result))

    if isinstance(effect, EffectCloseDoor):
        result = attempt(lambda: deps.device_door.close())
        msg_queue.put(MsgDoorCloseDone(result=result))
