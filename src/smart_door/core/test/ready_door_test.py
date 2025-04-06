from datetime import datetime
from src.image_classifier.bounding_box import BoundingBox
from src.image_classifier.classification import Classification
from src.smart_door.core.model import DoorState, ModelReady
from src.smart_door.core.msg import MsgTick
from src.smart_door.core.test.fixture import Fixture


def test_transition_to_will_open_state_when_classifications_contain_unlock_list_objects() -> (
    None
):
    f = Fixture()

    model, _ = f.init()

    model, _ = f.transition_to_ready_state(model=model)

    classifications = [
        Classification(
            label="person",
        ),
        Classification(
            label="cat",
        ),
    ]

    model.camera.latest_classification = classifications

    model, _ = f.transition(model=model, msg=MsgTick(happened_at=datetime.now()))

    assert isinstance(model, ModelReady)
    assert model.door.state == DoorState.WillOpen
