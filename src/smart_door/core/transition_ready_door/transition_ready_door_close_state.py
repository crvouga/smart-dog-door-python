from dataclasses import replace
from src.image_classifier.classification import Classification
from src.image_classifier.classification_config import ClassificationConfig
from ..model import (
    DoorState,
    ModelDoor,
    ModelReady,
    to_latest_classifications,
)
from ..msg import (
    Msg,
    MsgTick,
)
from ..effect import (
    Effect,
    EffectCloseDoor,
)


def transition_ready_door_close(
    model: ModelReady, door: ModelDoor, msg: Msg
) -> tuple[ModelDoor, list[Effect]]:
    effects_new: list[Effect] = []

    door, effects = _transition_to_will_close(model=model, door=door, msg=msg)
    effects_new.extend(effects)

    door, effects = _transition_from_will_close_to_closed(
        model=model, door=door, msg=msg
    )
    effects_new.extend(effects)

    return door, effects_new


def _transition_to_will_close(
    model: ModelReady, door: ModelDoor, msg: Msg
) -> tuple[ModelDoor, list[Effect]]:
    should_close = _does_have_close_list_objects(
        classifications=to_latest_classifications(model=model),
        close_list=model.config.classification_close_list,
    )

    if should_close and door.state == DoorState.WillOpen:
        return (
            replace(door, state=DoorState.Closed, state_start_time=msg.happened_at),
            [],
        )

    if should_close and door.state == DoorState.Opened:
        return (
            replace(door, state=DoorState.WillClose, state_start_time=msg.happened_at),
            [],
        )

    return door, []


def _transition_from_will_close_to_closed(
    model: ModelReady, door: ModelDoor, msg: Msg
) -> tuple[ModelDoor, list[Effect]]:
    if not isinstance(msg, MsgTick):
        return door, []

    if door.state != DoorState.WillClose:
        return door, []

    elapsed_time = msg.happened_at - door.state_start_time

    should_close = elapsed_time >= model.config.minimal_duration_will_close

    if not should_close:
        return door, []

    return (
        replace(door, state=DoorState.Closed, state_start_time=msg.happened_at),
        [EffectCloseDoor()],
    )


def _does_have_close_list_objects(
    classifications: list[Classification],
    close_list: list[ClassificationConfig],
) -> bool:
    return any(
        _does_have_close_list_object(
            classifications=classifications,
            close_object=close_object,
        )
        for close_object in close_list
    )


def _does_have_close_list_object(
    classifications: list[Classification],
    close_object: ClassificationConfig,
) -> bool:
    return any(
        classification.label.lower().strip() == close_object.label.lower().strip()
        and classification.weight >= close_object.min_weight
        for classification in classifications
    )
