from datetime import datetime
from src.device_camera.event import EventCamera
from src.smart_door.core.model import ClassificationRun, Model
from .core import (
    Effect,
    Msg,
    EffectCaptureImage,
    EffectClassifyImages,
    EffectSubscribeCamera,
    EffectSubscribeDoor,
    EffectSubscribeTick,
    EffectOpenDoor,
    EffectCloseDoor,
    MsgImageCaptureDone,
    MsgImageClassifyDone,
    MsgDoorOpenDone,
    MsgDoorCloseDone,
    MsgTick,
    MsgDoorEvent,
    MsgCameraEvent,
)
import queue
from .deps import Deps
from src.library.time import ticks


def interpret_effect(
    deps: Deps, model: Model, effect: Effect, msg_queue: queue.Queue[Msg]
) -> None:
    if isinstance(effect, EffectSubscribeCamera):
        deps.device_camera.events().subscribe(
            lambda camera_event: msg_queue.put(
                MsgCameraEvent(camera_event=camera_event)
            )
        )

    if isinstance(effect, EffectSubscribeDoor):
        deps.device_door.events().subscribe(
            lambda door_event: msg_queue.put(MsgDoorEvent(door_event=door_event))
        )

    if isinstance(effect, EffectSubscribeTick):
        ticks(interval=model.config.tick_rate).subscribe(
            lambda now: msg_queue.put(MsgTick(happened_at=now))
        )

    if isinstance(effect, EffectCaptureImage):
        images = deps.device_camera.capture()
        msg_queue.put(MsgImageCaptureDone(images=images))

    if isinstance(effect, EffectClassifyImages):
        classifications = deps.image_classifier.classify(images=effect.images)
        finished_at = datetime.now()
        msg_queue.put(
            MsgImageClassifyDone(
                classification_run=ClassificationRun(
                    classifications=classifications,
                    images=effect.images,
                    finished_at=finished_at,
                )
            )
        )

    if isinstance(effect, EffectOpenDoor):
        deps.device_door.open()
        msg_queue.put(MsgDoorOpenDone())

    if isinstance(effect, EffectCloseDoor):
        deps.device_door.close()
        msg_queue.put(MsgDoorCloseDone())
