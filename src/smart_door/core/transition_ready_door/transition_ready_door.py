from ..model import (
    ModelDoor,
    ModelReady,
)
from ..msg import (
    Msg,
)
from ..effect import (
    Effect,
)
from .transition_ready_door_open_state import transition_ready_door_open
from .transition_ready_door_close_state import transition_ready_door_close
from .transition_ready_door_default_state import transition_ready_door_default_state


def transition_ready_door(
    model: ModelReady, door: ModelDoor, msg: Msg
) -> tuple[ModelDoor, list[Effect]]:
    effects_new: list[Effect] = []

    door, effects = transition_ready_door_open(model=model, door=door, msg=msg)
    effects_new.extend(effects)

    door, effects = transition_ready_door_close(model=model, door=door, msg=msg)
    effects_new.extend(effects)

    door, effects = transition_ready_door_default_state(model=model, door=door, msg=msg)
    effects_new.extend(effects)

    return door, effects_new
