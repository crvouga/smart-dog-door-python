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
    EffectCloseDoor,
    EffectOpenDoor,
)


def transition_ready_door(
    model: ModelReady, door: ModelDoor, msg: Msg
) -> tuple[ModelDoor, list[Effect]]:
    effects_new: list[Effect] = []

    door, effects = _transition_door_to_will_open(model=model, door=door, msg=msg)
    effects_new.extend(effects)

    door, effects = _transition_from_will_open_to_open(model=model, door=door, msg=msg)
    effects_new.extend(effects)

    door, effects = _transition_door_to_will_close(model=model, door=door, msg=msg)
    effects_new.extend(effects)

    door, effects = _transition_from_will_close_to_closed(
        model=model, door=door, msg=msg
    )
    effects_new.extend(effects)

    return door, effects_new


def _transition_door_to_will_close(
    model: ModelReady, door: ModelDoor, msg: Msg
) -> tuple[ModelDoor, list[Effect]]:
    should_close = _does_have_close_list_objects(
        classifications=model.camera.latest_classification,
        close_list=model.config.classification_close_list,
    )

    if not should_close:
        return door, []

    if door.state == DoorState.Closed:
        return door, []

    if door.state == DoorState.WillOpen:
        return replace(door, state=DoorState.Closed), []

    return replace(door, state=DoorState.WillClose), []


def _transition_from_will_close_to_closed(
    model: ModelReady, door: ModelDoor, msg: Msg
) -> tuple[ModelDoor, list[Effect]]:
    if door.state != DoorState.WillClose:
        return door, []

    if not isinstance(msg, MsgTick):
        return door, []

    elapsed_time = msg.happened_at - door.state_start_time
    if elapsed_time < model.config.minimal_duration_will_close:
        return door, []

    return replace(door, state=DoorState.Closed), [EffectCloseDoor()]


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

    return replace(door, state=DoorState.Open), [EffectOpenDoor()]


def _transition_door_to_will_open(
    model: ModelReady, door: ModelDoor, msg: Msg
) -> tuple[ModelDoor, list[Effect]]:
    should_open = _does_have_open_list_objects(
        classifications=model.camera.latest_classification,
        open_list=model.config.classification_open_list,
    )

    if not should_open:
        return door, []

    if door.state == DoorState.Open:
        return door, []

    if door.state == DoorState.WillClose:
        return replace(door, state=DoorState.Open), []

    if door.state == DoorState.Closed:
        return replace(door, state=DoorState.WillOpen), []

    if door.state == DoorState.WillOpen:
        return replace(door, state=DoorState.WillOpen), []

    return door, []


def _does_have_open_list_objects(
    classifications: list[Classification],
    open_list: list[ClassificationConfig],
) -> bool:
    return any(
        _does_have_open_list_object(
            classifications=classifications,
            open_object=open_object,
        )
        for open_object in open_list
    )


def _does_have_open_list_object(
    classifications: list[Classification],
    open_object: ClassificationConfig,
) -> bool:
    return any(
        classification.label.lower().strip() == open_object.label.lower().strip()
        and classification.weight >= open_object.min_weight
        for classification in classifications
    )
