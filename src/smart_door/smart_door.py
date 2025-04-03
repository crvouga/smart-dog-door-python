from src.image_classifier.interface import ImageClassifier
from src.library.state_machine import StateMachine
from .core import init, transition, Effect
from .interpret_effect import interpret_effect
from dataclasses import dataclass


@dataclass
class SmartDoor:
    image_classifier: ImageClassifier

    @classmethod
    def start(cls, smart_door: "SmartDoor") -> None:
        state_machine = StateMachine(
            init=init,
            transition=transition,
            interpret_effect=lambda effect, msg_queue: interpret_effect(
                smart_door=smart_door,
                effect=effect,
                msg_queue=msg_queue,
            ),
        )

        state_machine.start()
