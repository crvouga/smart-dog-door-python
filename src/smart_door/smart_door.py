from logging import Logger
import queue
from src.image_classifier.interface import ImageClassifier
from src.device_camera.interface import DeviceCamera
from src.device_door.interface import DeviceDoor
from src.library.life_cycle import LifeCycle
from src.library.state_machine import StateMachine
from src.smart_door.core.effect import Effect
from src.smart_door.core.msg import Msg
from .core import init, transition
from .interpret_effect import interpret_effect
from .deps import Deps


class SmartDoor(LifeCycle):
    deps: Deps
    _resources: list[LifeCycle]

    def __init__(
        self,
        image_classifier: ImageClassifier,
        device_camera: DeviceCamera,
        device_door: DeviceDoor,
        logger: Logger,
    ) -> None:
        self.deps = Deps(
            image_classifier=image_classifier,
            device_camera=device_camera,
            device_door=device_door,
            logger=logger.getChild("smart_door"),
        )

        self.state_machine = StateMachine(
            init=init,
            transition=transition,
            interpret_effect=self._interpret_effect,
            logger=self.deps.logger,
        )

        self._resources = [
            self.deps.device_camera,
            self.deps.device_door,
            self.state_machine,
        ]

    def _interpret_effect(self, effect: Effect, msg_queue: queue.Queue[Msg]) -> None:
        interpret_effect(deps=self.deps, effect=effect, msg_queue=msg_queue)

    def start(self) -> None:
        self.deps.logger.info("Starting")
        for resource in self._resources:
            resource.start()
        self.deps.logger.info("Started")

    def stop(self) -> None:
        self.deps.logger.info("Stopping")
        for resource in reversed(self._resources):
            resource.stop()
        self.deps.logger.info("Stopped")
