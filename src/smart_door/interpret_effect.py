from src.device_camera.event import EventCamera
from .core import (
    Effect,
    Msg,
    EffectCaptureFrames,
    EffectClassifyImages,
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
import queue
from .deps import Deps
from src.library.time import ticks


def interpret_effect(deps: Deps, effect: Effect, msg_queue: queue.Queue[Msg]) -> None:
    if isinstance(effect, EffectSubscribeCamera):
        deps.device_camera.events().sub(
            lambda camera_event: msg_queue.put(
                MsgCameraEvent(camera_event=camera_event)
            )
        )

    if isinstance(effect, EffectSubscribeDoor):
        deps.device_door.events().sub(
            lambda door_event: msg_queue.put(MsgDoorEvent(door_event=door_event))
        )

    if isinstance(effect, EffectSubscribeTick):
        ticks(interval_seconds=1).sub(lambda now: msg_queue.put(MsgTick(now=now)))

    if isinstance(effect, EffectCaptureFrames):
        images = deps.device_camera.capture()
        msg_queue.put(MsgFramesCaptureDone(images=images))

    if isinstance(effect, EffectClassifyImages):
        classifications = deps.image_classifier.classify(images=effect.images)
        msg_queue.put(MsgFramesClassifyDone(classifications=classifications))

    if isinstance(effect, EffectOpenDoor):
        deps.device_door.open()
        msg_queue.put(MsgDoorOpenDone())

    if isinstance(effect, EffectCloseDoor):
        deps.device_door.close()
        msg_queue.put(MsgDoorCloseDone())
