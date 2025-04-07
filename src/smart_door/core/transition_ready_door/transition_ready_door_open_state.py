from dataclasses import replace
from src.image_classifier.classification import Classification
from src.image_classifier.classification_config import ClassificationConfig
from ..model import (
    DoorState,
    ModelDoor,
    ModelReady,
)
from ..msg import (
    Msg,
    MsgTick,
)
from ..effect import (
    Effect,
    EffectOpenDoor,
)


def transition_ready_door_open(
    model: ModelReady, door: ModelDoor, msg: Msg
) -> tuple[ModelDoor, list[Effect]]:
    effects_new: list[Effect] = []

    door, effects = _transition_to_will_open(model=model, door=door, msg=msg)
    effects_new.extend(effects)

    door, effects = _transition_from_will_open_to_opened(
        model=model, door=door, msg=msg
    )
    effects_new.extend(effects)

    return door, effects_new


def _transition_from_will_open_to_opened(
    model: ModelReady, door: ModelDoor, msg: Msg
) -> tuple[ModelDoor, list[Effect]]:
    if not isinstance(msg, MsgTick):
        return door, []

    if door.state != DoorState.WillOpen:
        return door, []

    elapsed_time = msg.happened_at - door.state_start_time

    should_open = elapsed_time >= model.config.minimal_duration_will_open

    if not should_open:
        return door, []

    return (
        replace(door, state=DoorState.Opened, state_start_time=msg.happened_at),
        [EffectOpenDoor()],
    )


def _transition_to_will_open(
    model: ModelReady, door: ModelDoor, msg: Msg
) -> tuple[ModelDoor, list[Effect]]:
    should_open = _does_have_open_list_objects(
        classifications=model.camera.latest_classification,
        open_list=model.config.classification_open_list,
    )

    if not should_open and door.state == DoorState.WillOpen:
        return (
            replace(
                door,
                state=DoorState.Closed,
                state_start_time=msg.happened_at,
            ),
            [],
        )

    if should_open and door.state == DoorState.Opened:
        return door, []

    if should_open and door.state == DoorState.WillClose:
        return (
            replace(door, state=DoorState.Opened, state_start_time=msg.happened_at),
            [],
        )

    if should_open and door.state == DoorState.Closed:
        return (
            replace(door, state=DoorState.WillOpen, state_start_time=msg.happened_at),
            [],
        )

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
