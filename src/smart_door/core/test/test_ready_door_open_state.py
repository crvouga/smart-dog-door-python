from datetime import datetime, timedelta
from dataclasses import replace
from src.image_classifier.classification import Classification
from src.smart_door.core.effect import EffectOpenDoor
from src.smart_door.core.model import DoorState, Model, ModelReady
from src.smart_door.core.msg import MsgTick
from src.smart_door.core.test.fixture import BaseFixture


class Fixture(BaseFixture):
    def __init__(self, door_state: DoorState = DoorState.Closed) -> None:
        super().__init__()
        model, _ = self.init()
        model, _ = self.transition_to_ready_state(model=model)

        classifications = [
            Classification(
                label="dog",
                weight=0.5,
            ),
        ]

        self.model = replace(
            model,
            door=replace(model.door, state=door_state, state_start_time=datetime.now()),
            camera=replace(model.camera, latest_classification=classifications),
        )


def test_transition_to_will_open_state_when_classifications_contain_unlock_list_objects() -> (
    None
):
    f = Fixture()
    model, _ = f.transition(model=f.model, msg=MsgTick(happened_at=datetime.now()))

    assert isinstance(model, ModelReady)
    assert model.door.state == DoorState.WillOpen


def test_do_not_transition_to_will_open_state_if_door_is_already_open() -> None:
    f = Fixture(door_state=DoorState.Opened)
    model, _ = f.transition(model=f.model, msg=MsgTick(happened_at=datetime.now()))

    assert isinstance(model, ModelReady)
    assert model.door.state == DoorState.Opened


def test_transition_to_open_state_if_state_is_will_close() -> None:
    f = Fixture(door_state=DoorState.WillClose)
    model, _ = f.transition(model=f.model, msg=MsgTick(happened_at=datetime.now()))

    assert isinstance(model, ModelReady)
    assert model.door.state == DoorState.Opened


def test_transition_to_open_state_after_minimal_duration_will_open() -> None:
    f = Fixture(door_state=DoorState.WillOpen)
    assert isinstance(f.model, ModelReady)

    happened_at = (
        f.model.door.state_start_time
        + f.model.config.minimal_duration_will_open
        + timedelta(seconds=1)
    )

    model, effects = f.transition(
        model=f.model,
        msg=MsgTick(happened_at=happened_at),
    )

    assert isinstance(model, ModelReady)
    assert model.door.state == DoorState.Opened
    assert model.door.state_start_time == happened_at
    assert any(isinstance(effect, EffectOpenDoor) for effect in effects)
