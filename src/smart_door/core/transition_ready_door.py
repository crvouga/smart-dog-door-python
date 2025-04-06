from .model import (
    ModelDoor,
    ModelReady,
    ModelCamera,
    CameraState,
)
from .msg import (
    Msg,
    MsgImageCaptureDone,
    MsgImageClassifyDone,
    MsgTick,
)
from .effect import (
    Effect,
    EffectCaptureImage,
    EffectClassifyImages,
)


def transition_ready_door(
    model: ModelReady, door: ModelDoor, msg: Msg
) -> tuple[ModelDoor, list[Effect]]:
    return door, []
