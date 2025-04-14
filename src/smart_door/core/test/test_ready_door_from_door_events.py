from datetime import datetime, timedelta
from dataclasses import replace
from src.image_classifier.classification import Classification
from src.device_door.event import EventDoorOpened, EventDoorClosed
from src.smart_door.core.effect import EffectCloseDoor
from src.smart_door.core.model import DoorState, ModelReady
from src.smart_door.core.msg import MsgTick, MsgDoorEvent
from src.smart_door.core.test.fixture import BaseFixture


class Fixture(BaseFixture):
    def __init__(
        self,
        door_state: DoorState,
        classifications: list[Classification],
    ) -> None:
        super().__init__()
        model, _ = self.init()
        model, _ = self.transition_to_ready_state(model=model)

        self.model = replace(
            model,
            door=replace(model.door, state=door_state, state_start_time=datetime.now()),
            camera=replace(model.camera, latest_classification=classifications),
        )


def test_transition_to_opened_state_when_door_opened_event_received() -> None:
    f = Fixture(door_state=DoorState.Closed, classifications=[])
    happened_at = datetime.now()
    model, _ = f.transition(
        model=f.model,
        msg=MsgDoorEvent(happened_at=happened_at, door_event=EventDoorOpened()),
    )

    assert isinstance(model, ModelReady)
    assert model.door.state == DoorState.Opened
    assert model.door.state_start_time == happened_at


# def test_transition_to_closed_state_when_door_closed_event_received() -> None:
#     f = Fixture(door_state=DoorState.Opened, classifications=[])
#     happened_at = datetime.now()
#     model, _ = f.transition(
#         model=f.model,
#         msg=MsgDoorEvent(happened_at=happened_at, door_event=EventDoorClosed()),
#     )

#     assert isinstance(model, ModelReady)
#     assert model.door.state == DoorState.Closed
#     assert model.door.state_start_time == happened_at


# def test_door_opened_event_cancels_will_close_state() -> None:
#     f = Fixture(door_state=DoorState.WillClose, classifications=[])
#     happened_at = datetime.now()
#     model, _ = f.transition(
#         model=f.model,
#         msg=MsgDoorEvent(happened_at=happened_at, door_event=EventDoorOpened()),
#     )

#     assert isinstance(model, ModelReady)
#     assert model.door.state == DoorState.Opened
#     assert model.door.state_start_time == happened_at


# def test_door_closed_event_cancels_will_open_state() -> None:
#     f = Fixture(door_state=DoorState.WillOpen, classifications=[])
#     happened_at = datetime.now()
#     model, _ = f.transition(
#         model=f.model,
#         msg=MsgDoorEvent(happened_at=happened_at, door_event=EventDoorClosed()),
#     )

#     assert isinstance(model, ModelReady)
#     assert model.door.state == DoorState.Closed
#     assert model.door.state_start_time == happened_at
