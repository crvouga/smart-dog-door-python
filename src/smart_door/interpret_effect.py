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
)
import queue
from .deps import Deps


def interpret_effect(deps: Deps, effect: Effect, msg_queue: queue.Queue[Msg]) -> None:
    if isinstance(effect, EffectSubscribeCamera):
        pass

    if isinstance(effect, EffectSubscribeDoor):
        pass

    if isinstance(effect, EffectSubscribeTick):
        pass

    if isinstance(effect, EffectCaptureFrames):
        pass

    if isinstance(effect, EffectClassifyFrames):
        pass

    if isinstance(effect, EffectOpenDoor):
        pass

    if isinstance(effect, EffectCloseDoor):
        pass
