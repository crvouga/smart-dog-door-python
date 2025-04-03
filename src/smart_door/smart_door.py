from src.image_classifier.interface import ImageClassifier
from src.library.state_machine import StateMachine
from .core import init, transition
from .interpret_effect import interpret_effect
from .deps import Deps


class SmartDoor:
    deps: Deps

    def __init__(self, image_classifier: ImageClassifier) -> None:
        self.deps = Deps(image_classifier=image_classifier)
        self.state_machine = StateMachine(
            init=init,
            transition=transition,
            interpret_effect=lambda effect, msg_queue: interpret_effect(
                deps=self.deps,
                effect=effect,
                msg_queue=msg_queue,
            ),
        )

    def start(self) -> None:
        self.state_machine.start()
