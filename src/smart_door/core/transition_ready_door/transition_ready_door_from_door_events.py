from dataclasses import replace

from src.device_door.event import EventDoorClosed, EventDoorOpened
from ..model import (
    DoorState,
    ModelDoor,
    ModelReady,
)
from ..msg import (
    Msg,
    MsgDoorEvent,
)
from ..effect import (
    Effect,
)


def transition_ready_door_from_door_events(
    model: ModelReady, door: ModelDoor, msg: Msg
) -> tuple[ModelDoor, list[Effect]]:
    if not isinstance(msg, MsgDoorEvent):
        return door, []

    if isinstance(msg.door_event, EventDoorOpened):
        door_new = replace(
            door, state=DoorState.Opened, state_start_time=msg.happened_at
        )
        return door_new, []

    if isinstance(msg.door_event, EventDoorClosed):
        door_new = replace(
            door, state=DoorState.Closed, state_start_time=msg.happened_at
        )
        return door_new, []

    return door, []
