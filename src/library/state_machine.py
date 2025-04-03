from typing import Callable, Generic, TypeVar
import queue


Model = TypeVar("Model")
Msg = TypeVar("Msg")
Effect = TypeVar("Effect")


class StateMachine(Generic[Model, Msg, Effect]):
    def __init__(
        self,
        init: Callable[[], Model],
        transition: Callable[[Model, Msg], tuple[Model, list[Effect]]],
        interpret_effect: Callable[[Effect], None],
    ):
        self.init = init
        self.transition = transition
        self.interpret_effect = interpret_effect
        self.msg_queue = queue.Queue[Msg]()

    # def start(self):
