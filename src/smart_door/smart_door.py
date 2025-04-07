from logging import Logger
import queue
from src.image_classifier.interface import ImageClassifier
from src.device_camera.interface import DeviceCamera
from src.device_door.interface import DeviceDoor
from src.library.life_cycle import LifeCycle
from src.library.pub_sub import Sub
from src.library.state_machine import StateMachine
from src.smart_door.config import Config
from src.smart_door.core import transition, init
from src.smart_door.core.effect import Effect
from src.smart_door.core.model import Model
from src.smart_door.core.msg import Msg
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

        self._state_machine = StateMachine(
            init=init,
            transition=transition,
            interpret_effect=self._interpret_effect,
            logger=self._deps.logger,
        )

    @property
    def models(self) -> Sub[Model]:
        return self._state_machine.models()

    @property
    def msgs(self) -> Sub[Msg]:
        return self._state_machine.msgs()

    def _interpret_effect(
        self, model: Model, effect: Effect, msg_queue: queue.Queue[Msg]
    ) -> None:
        interpret_effect(
            deps=self._deps,
            model=model,
            effect=effect,
            msg_queue=msg_queue,
        )

    def start(self) -> None:
        self._deps.logger.info("Starting")
        self._state_machine.start()
        self._deps.logger.info("Started")

    def stop(self) -> None:
        self._deps.logger.info("Stopping")
        self._state_machine.stop()
        self._deps.logger.info("Stopped")
