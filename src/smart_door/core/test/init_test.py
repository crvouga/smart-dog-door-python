from src.smart_door.core import (
    ConnectionState,
    EffectSubscribeCamera,
    EffectSubscribeDoor,
    EffectSubscribeTick,
)
from src.smart_door.core.test.fixture import Fixture


def test_init() -> None:
    f = Fixture()

    model, effects = f.t.init()

    assert model.type == "connecting"
    assert model.camera == ConnectionState.Connecting
    assert model.door == ConnectionState.Connecting

    assert len(effects) == 3
    assert isinstance(effects[0], EffectSubscribeCamera)
    assert isinstance(effects[1], EffectSubscribeDoor)
    assert isinstance(effects[2], EffectSubscribeTick)
