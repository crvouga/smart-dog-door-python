from logging import Logger
import queue
from src.image_classifier.interface import ImageClassifier
from src.device_camera.interface import DeviceCamera
from src.device_door.interface import DeviceDoor
from src.library.life_cycle import LifeCycle
from src.library.pub_sub import Sub
from src.library.state_machine import StateMachine
from src.smart_door.config import Config
from src.smart_door.core.effect import Effect
from src.smart_door.core.model import Model
from src.smart_door.core.msg import Msg
from .core import Transition
from .interpret_effect import interpret_effect
from .deps import Deps


class SmartDoor(LifeCycle):
    _deps: Deps
    _state_machine: StateMachine

    def __init__(
        self,
        image_classifier: ImageClassifier,
        device_camera: DeviceCamera,
        device_door: DeviceDoor,
        logger: Logger,
    ) -> None:
        self._deps = Deps(
            image_classifier=image_classifier,
            device_camera=device_camera,
            device_door=device_door,
            logger=logger.getChild("smart_door"),
        )

        t = Transition(config=Config())

        self._state_machine = StateMachine(
            init=t.init,
            transition=t.transition,
            interpret_effect=self._interpret_effect,
            logger=self._deps.logger,
        )

    def models(self) -> Sub[Model]:
        return self._state_machine.models()

    def _interpret_effect(self, effect: Effect, msg_queue: queue.Queue[Msg]) -> None:
        interpret_effect(deps=self._deps, effect=effect, msg_queue=msg_queue)

    def start(self) -> None:
        self._deps.logger.info("Starting")
        self._state_machine.start()
        self._deps.logger.info("Started")

    def stop(self) -> None:
        self._deps.logger.info("Stopping")
        self._state_machine.stop()
        self._deps.logger.info("Stopped")
