from typing import Callable, Generic, TypeVar, Optional
import queue
import threading

Model = TypeVar("Model")
Msg = TypeVar("Msg")
Effect = TypeVar("Effect")


class StateMachine(Generic[Model, Msg, Effect]):
    init: Callable[[], Model]
    transition: Callable[[Model, Msg], tuple[Model, list[Effect]]]
    interpret_effect: Callable[[Effect], None]
    msg_queue: queue.Queue[Msg]
    model: Optional[Model]

    def __init__(
        self,
        init: Callable[[], Model],
        transition: Callable[[Model, Msg], tuple[Model, list[Effect]]],
        interpret_effect: Callable[[Effect, queue.Queue[Msg]], None],
    ) -> None:
        self.init = init
        self.transition = transition
        self.interpret_effect = interpret_effect
        self.msg_queue = queue.Queue[Msg]()
        self.model = None

    def _interpret_effect(self, effect: Effect) -> None:
        thread = threading.Thread(
            target=self.interpret_effect, args=(effect, self.msg_queue)
        )
        thread.start()
        thread.join()

    def start(self) -> None:
        model, effects = self.init()

        self.model = model

        for effect in effects:
            self._interpret_effect(effect)

        while True:
            msg = self.msg_queue.get()

            model, effects = self.transition(self.model, msg)

            self.model = model

            for effect in effects:
                self._interpret_effect(effect)
