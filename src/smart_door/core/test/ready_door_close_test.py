from datetime import datetime, timedelta
from dataclasses import replace
from src.image_classifier.classification import Classification
from src.smart_door.core.model import DoorState, ModelReady
from src.smart_door.core.msg import MsgTick
from src.smart_door.core.test.fixture import BaseFixture


class Fixture(BaseFixture):
    def __init__(self, door_state: DoorState = DoorState.Closed) -> None:
        super().__init__()
        model, _ = self.init()
        model, _ = self.transition_to_ready_state(model=model)

        classifications = [
            Classification(
                label="cat",
                weight=0.5,
            ),
        ]

        self.model = replace(
            model,
            door=replace(model.door, state=door_state, state_start_time=datetime.now()),
            camera=replace(model.camera, latest_classification=classifications),
        )


def test_transition_to_will_close_state_when_open() -> None:
    f = Fixture(door_state=DoorState.Open)
    model, _ = f.transition(model=f.model, msg=MsgTick(happened_at=datetime.now()))

    assert isinstance(model, ModelReady)
    assert model.door.state == DoorState.WillClose


def test_stays_in_closed_state() -> None:
    f = Fixture(door_state=DoorState.Closed)
    model, _ = f.transition(model=f.model, msg=MsgTick(happened_at=datetime.now()))

    assert isinstance(model, ModelReady)
    assert model.door.state == DoorState.Closed


def test_transition_to_closed_state_if_door_state_is_will_open() -> None:
    f = Fixture(door_state=DoorState.WillOpen)
    model, _ = f.transition(model=f.model, msg=MsgTick(happened_at=datetime.now()))

    assert isinstance(model, ModelReady)
    assert model.door.state == DoorState.Closed


def test_transition_to_will_open_state_if_door_state_is_open() -> None:
    f = Fixture(door_state=DoorState.WillOpen)
    model, _ = f.transition(model=f.model, msg=MsgTick(happened_at=datetime.now()))

    assert isinstance(model, ModelReady)
    assert model.door.state == DoorState.Closed


def test_transition_to_will_close_state_to_closed_state_after_minimal_duration_will_close() -> (
    None
):
    f = Fixture(door_state=DoorState.WillClose)

    model, _ = f.transition(
        model=f.model,
        msg=MsgTick(
            happened_at=datetime.now() + f.model.config.minimal_duration_will_close
        ),
    )

    assert isinstance(model, ModelReady)
    assert model.door.state == DoorState.Closed
