from src.smart_door.core.transition_connecting import transition_connecting
from src.smart_door.core.transition_ready import transition_ready
from .model import (
    Model,
    ModelConnecting,
    ModelReady,
    ConnectionState,
)
from .msg import (
    Msg,
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
            camera=ConnectionState.Connecting,
            door=ConnectionState.Connecting,
        ),
        [
            EffectSubscribeCamera(),
            EffectSubscribeDoor(),
            EffectSubscribeTick(),
        ],
    )


def transition(model: Model, msg: Msg) -> tuple[Model, list[Effect]]:
    if isinstance(model, ModelConnecting):
        return transition_connecting(model=model, msg=msg)

    if isinstance(model, ModelReady):
        return transition_ready(model=model, msg=msg)

    return model, []
