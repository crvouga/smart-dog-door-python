from .model import (
    Model,
    ModelConnecting,
    ConnectionState,
)
from .effect import (
    Effect,
    EffectSubscribeCamera,
    EffectSubscribeDoor,
    EffectSubscribeTick,
)


def init() -> tuple[Model, list[Effect]]:
    return (
        ModelConnecting(
            type="connecting",
            camera=ConnectionState.Connecting,
            door=ConnectionState.Connecting,
        ),
        [
            EffectSubscribeCamera(type="subscribe_camera"),
            EffectSubscribeDoor(type="subscribe_door"),
            EffectSubscribeTick(type="subscribe_tick"),
        ],
    )
