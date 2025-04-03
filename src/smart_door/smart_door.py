from src.library.state_machine import StateMachine
from .core import init, transition, Effect
from .interpret_effect import interpret_effect


class SmartDoor:
    def __init__(self):
        self.state_machine = StateMachine(
            init=init,
            transition=transition,
            interpret_effect=interpret_effect,
        )
