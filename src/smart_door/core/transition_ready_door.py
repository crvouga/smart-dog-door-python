from src.image_classifier.classification import Classification
from .model import (
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

    model.config.classification_open_list

    return door, []


def does_have_open_list_objects(
    classifications: list[Classification],
    open_list: list[str],
) -> bool:
    return any(classification.label in open_list for classification in classifications)
