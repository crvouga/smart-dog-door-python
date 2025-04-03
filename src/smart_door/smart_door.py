import queue
from src.image_classifier.interface import ImageClassifier
from src.device_camera.interface import DeviceCamera
from src.device_door.interface import DeviceDoor
from src.library.state_machine import StateMachine
from src.smart_door.core.effect import Effect
from src.smart_door.core.msg import Msg
from .core import init, transition
from .interpret_effect import interpret_effect
from .deps import Deps


class SmartDoor:
    deps: Deps

    def __init__(
        self,
        image_classifier: ImageClassifier,
        device_camera: DeviceCamera,
        device_door: DeviceDoor,
    ) -> None:
        self.deps = Deps(
            image_classifier=image_classifier,
            device_camera=device_camera,
            device_door=device_door,
        )
        self.state_machine = StateMachine(
            init=init, transition=transition, interpret_effect=self._interpret_effect
        )

    def _interpret_effect(self, effect: Effect, msg_queue: queue.Queue[Msg]) -> None:
        interpret_effect(deps=self.deps, effect=effect, msg_queue=msg_queue)

    def start(self) -> None:
        self.state_machine.start()
