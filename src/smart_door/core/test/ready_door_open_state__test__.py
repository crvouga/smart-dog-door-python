from datetime import datetime, timedelta
from dataclasses import replace
from src.image_classifier.classification import Classification
from src.smart_door.core.effect import EffectOpenDoor
from src.smart_door.core.model import ClassificationRun, DoorState, Model, ModelReady
from src.smart_door.core.msg import MsgImageClassifyDone, MsgTick, MsgImageCaptureDone
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
            camera=replace(
                model.camera,
                classification_runs=[
                    ClassificationRun(
                        classifications=classifications,
                        images=[],
                        finished_at=datetime.now(),
                    ),
                ],
            ),
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


def test_bail_on_will_open_if_no_object_is_detected() -> None:
    f = Fixture(door_state=DoorState.WillOpen)
    model, _ = f.transition(
        model=f.model,
        msg=MsgTick(happened_at=datetime.now()),
    )
    assert isinstance(model, ModelReady)
    assert model.door.state == DoorState.WillOpen

    model, _ = f.transition(
        model=replace(
            model,
            camera=replace(
                model.camera,
                classification_runs=[
                    ClassificationRun(
                        classifications=[], images=[], finished_at=datetime.now()
                    )
                ],
            ),
        ),
        msg=MsgTick(happened_at=datetime.now()),
    )

    assert isinstance(model, ModelReady)
    assert model.door.state == DoorState.Closed


def test_bail_on_will_close_if_open_object_is_detected() -> None:
    f = Fixture(door_state=DoorState.WillClose)
    model: Model = replace(
        f.model,
        camera=replace(
            f.model.camera,
            classification_runs=[
                ClassificationRun(
                    classifications=[], images=[], finished_at=datetime.now()
                ),
            ],
        ),
    )
    model, _ = f.transition(
        model=model,
        msg=MsgTick(happened_at=datetime.now()),
    )
    assert isinstance(model, ModelReady)
    assert model.door.state == DoorState.WillClose

    model, _ = f.transition(
        model=replace(
            model,
            camera=replace(
                model.camera,
                classification_runs=[
                    ClassificationRun(
                        classifications=[
                            Classification(label="dog", weight=0.5),
                        ],
                        images=[],
                        finished_at=datetime.now(),
                    ),
                ],
            ),
        ),
        msg=MsgTick(happened_at=datetime.now()),
    )

    assert isinstance(model, ModelReady)
    assert model.door.state == DoorState.Opened


def test_transition_to_open_state_after_minimal_duration_will_open() -> None:
    f = Fixture(door_state=DoorState.WillOpen)

    happened_at = (
        f.model.door.state_start_time + f.model.config.minimal_duration_will_open
    )

    model, effects = f.transition(
        model=f.model,
        msg=MsgTick(happened_at=happened_at),
    )

    assert isinstance(model, ModelReady)
    assert model.door.state == DoorState.Opened
    assert model.door.state_start_time == happened_at
    assert any(isinstance(effect, EffectOpenDoor) for effect in effects)
