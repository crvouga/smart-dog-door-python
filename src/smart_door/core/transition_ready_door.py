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
)
from .effect import (
    Effect,
)


def transition_ready_door(
    model: ModelReady, door: ModelDoor, msg: Msg
) -> tuple[ModelDoor, list[Effect]]:

    should_open = does_have_open_list_objects(
        classifications=model.camera.latest_classification,
        open_list=model.config.classification_open_list,
    )

    if should_open and door.state != DoorState.Open:
        door_next_state = (
            DoorState.Open if door.state == DoorState.WillClose else DoorState.WillOpen
        )
        return replace(door, state=door_next_state), []

    return door, []


def does_have_open_list_objects(
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
