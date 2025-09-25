from datetime import datetime
from dataclasses import replace
from src.image_classifier.classification import Classification
from src.smart_door.core.model import ClassificationRun, DoorState, ModelReady
from src.smart_door.core.msg import MsgTick
from src.smart_door.core.test.fixture import BaseFixture


class Fixture(BaseFixture):
    def __init__(
        self,
        door_state: DoorState = DoorState.Closed,
    ) -> None:
        super().__init__()
        model, _ = self.init()
        model, _ = self.transition_to_ready_state(model=model)

        classifications = [
            Classification(label="cat", weight=0.5),
            Classification(label="dog", weight=0.5),
        ]

        self.model = replace(
            model,
            door=replace(model.door, state=door_state, state_start_time=datetime.now()),
            camera=replace(
                model.camera,
                classification_runs=[
                    ClassificationRun(
                        classifications=classifications,
                        images=[],
                        finished_at=datetime.now(),
                    )
                ],
            ),
        )


def test_close_objects_take_precedence_over_open_objects_when_closed() -> None:
    f = Fixture(door_state=DoorState.Closed)
    model, _ = f.transition(model=f.model, msg=MsgTick(happened_at=datetime.now()))

    assert isinstance(model, ModelReady)
    assert model.door.state == DoorState.Closed


def test_close_objects_take_precedence_over_open_objects_when_open() -> None:
    f = Fixture(door_state=DoorState.Opened)
    model, _ = f.transition(model=f.model, msg=MsgTick(happened_at=datetime.now()))

    assert isinstance(model, ModelReady)
    assert model.door.state == DoorState.WillClose


def test_close_objects_take_precedence_over_open_objects_when_will_open() -> None:
    f = Fixture(door_state=DoorState.WillOpen)
    model, _ = f.transition(model=f.model, msg=MsgTick(happened_at=datetime.now()))

    assert isinstance(model, ModelReady)
    assert model.door.state == DoorState.Closed


def test_close_objects_take_precedence_over_open_objects_when_will_close() -> None:
    f = Fixture(door_state=DoorState.WillClose)
    model, _ = f.transition(model=f.model, msg=MsgTick(happened_at=datetime.now()))

    assert isinstance(model, ModelReady)
    assert model.door.state == DoorState.WillClose
