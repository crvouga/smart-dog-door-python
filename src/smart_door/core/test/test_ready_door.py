from datetime import datetime, timedelta
from dataclasses import replace
from src.image_classifier.classification import Classification
from src.smart_door.core.model import DoorState, Model, ModelReady
from src.smart_door.core.msg import MsgTick
from src.smart_door.core.test.fixture import BaseFixture


class Fixture(BaseFixture):
    def __init__(
        self,
        door_state: DoorState = DoorState.Closed,
        classifications: list[Classification] = [],
    ) -> None:
        super().__init__()
        model, _ = self.init()
        model, _ = self.transition_to_ready_state(model=model)

        self.model = replace(
            model,
            door=replace(model.door, state=door_state, state_start_time=datetime.now()),
            camera=replace(model.camera, latest_classification=classifications),
        )


def test_close_objects_take_precedence_over_open_objects() -> None:
    f = Fixture(
        classifications=[
            Classification(label="cat", weight=0.5),
            Classification(label="dog", weight=0.5),
        ],
        door_state=DoorState.Closed,
    )
    model, _ = f.transition(model=f.model, msg=MsgTick(happened_at=datetime.now()))

    assert isinstance(model, ModelReady)
    assert model.door.state == DoorState.Closed
