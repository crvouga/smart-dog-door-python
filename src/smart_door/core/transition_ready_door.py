from dataclasses import replace
from src.image_classifier.classification import Classification
from src.image_classifier.classification_config import ClassificationConfig
from .model import (
    DoorState,
    ModelDoor,
    ModelReady,
)
from .msg import (
    Msg,
    MsgTick,
)
from .effect import (
    Effect,
)


def transition_ready_door(
    model: ModelReady, door: ModelDoor, msg: Msg
) -> tuple[ModelDoor, list[Effect]]:
    effects_new: list[Effect] = []

    door, effects = _transition_door_will_open(model=model, door=door, msg=msg)
    effects_new.extend(effects)

    door, effects = _transition_from_will_open_to_open(model=model, door=door, msg=msg)
    effects_new.extend(effects)

    return door, effects_new


def _transition_from_will_open_to_open(
    model: ModelReady, door: ModelDoor, msg: Msg
) -> tuple[ModelDoor, list[Effect]]:
    if door.state != DoorState.WillOpen:
        return door, []

    if not isinstance(msg, MsgTick):
        return door, []

    elapsed_time = msg.happened_at - door.state_start_time
    if elapsed_time < model.config.minimal_duration_will_open:
        return door, []

    return replace(door, state=DoorState.Open), []


def _transition_door_will_open(
    model: ModelReady, door: ModelDoor, msg: Msg
) -> tuple[ModelDoor, list[Effect]]:
    should_open = _does_have_open_list_objects(
        classifications=model.camera.latest_classification,
        open_list=model.config.classification_open_list,
    )

    if should_open and door.state != DoorState.Open:
        door_next_state = (
            DoorState.Open if door.state == DoorState.WillClose else DoorState.WillOpen
        )
        return replace(door, state=door_next_state), []

    return door, []


def _does_have_open_list_objects(
    classifications: list[Classification],
    open_list: list[ClassificationConfig],
) -> bool:
    return any(
        any(
            classification.label.lower().strip() == config.label.lower().strip()
            and classification.weight >= config.min_weight
            for classification in classifications
        )
        for config in open_list
    )
