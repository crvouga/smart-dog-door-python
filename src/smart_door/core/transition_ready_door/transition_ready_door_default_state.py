from dataclasses import replace
from ..model import (
    DoorState,
    ModelDoor,
    ModelReady,
    to_latest_classifications,
)
from ..msg import (
    Msg,
)
from ..effect import (
    Effect,
)


def transition_ready_door_default_state(
    model: ModelReady, door: ModelDoor, msg: Msg
) -> tuple[ModelDoor, list[Effect]]:
    effects_new: list[Effect] = []

    if door.state != DoorState.Opened:
        return door, effects_new

    classifications = to_latest_classifications(model=model)

    if len(classifications) != 0:
        return door, effects_new

    door_new = replace(
        door, state=DoorState.WillClose, state_start_time=msg.happened_at
    )

    return door_new, effects_new
