from datetime import datetime, timedelta
from dataclasses import replace
from src.image_classifier.classification import Classification
from src.smart_door.core.effect import EffectCloseDoor
from src.smart_door.core.model import DoorState, ModelReady
from src.smart_door.core.msg import MsgTick
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


def test_transition_to_will_close_state_when_door_is_open_and_no_classifications() -> (
    None
):
    f = Fixture(door_state=DoorState.Opened, classifications=[])
    happened_at = datetime.now()
    model, _ = f.transition(model=f.model, msg=MsgTick(happened_at=happened_at))

    assert isinstance(model, ModelReady)
    assert model.door.state == DoorState.WillClose
    assert model.door.state_start_time == happened_at
