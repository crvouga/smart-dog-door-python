from typing import Callable, Generic, TypeVar, Optional, List
import queue
import threading
from src.library.life_cycle import LifeCycle
import logging

Model = TypeVar("Model")
Msg = TypeVar("Msg")
Effect = TypeVar("Effect")


class StateMachine(Generic[Model, Msg, Effect], LifeCycle):
    _init: Callable[[], tuple[Model, List[Effect]]]
    _transition: Callable[[Model, Msg], tuple[Model, List[Effect]]]
    _interpret_effect: Callable[[Effect, queue.Queue[Msg]], None]
    _msg_queue: queue.Queue[Msg]
    _model: Optional[Model]
    _running: bool
    _thread: Optional[threading.Thread]
    _logger: logging.Logger

    def __init__(
        self,
        init: Callable[[], tuple[Model, List[Effect]]],
        transition: Callable[[Model, Msg], tuple[Model, List[Effect]]],
        interpret_effect: Callable[[Effect, queue.Queue[Msg]], None],
        logger: logging.Logger,
    ) -> None:
        self._init = init
        self._transition = transition
        self._interpret_effect = interpret_effect
        self._msg_queue = queue.Queue[Msg]()
        self._model = None
        self._running = False
        self._thread = None
        self._logger = logger.getChild("state_machine")

    def _interpret_effect_thread(self, effect: Effect) -> None:
        self._logger.debug("Interpreting effect: %s", effect)
        thread = threading.Thread(
            target=self._interpret_effect, args=(effect, self._msg_queue)
        )
        thread.start()
        thread.join()

    def _run(self) -> None:
        model, effects = self._init()

        self._model = model

        for effect in effects:
            self._interpret_effect_thread(effect)

        while self._running:
            try:
                msg = self._msg_queue.get(timeout=0.1)

                self._logger.debug("Received message: %s", msg)

                if msg is None:
                    self._running = False
                    break

                if self._model is not None:
                    model, effects = self._transition(self._model, msg)
                    self._model = model

                    for effect in effects:
                        self._interpret_effect_thread(effect)
            except queue.Empty:
                continue

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return

        self._running = True
        self._thread = threading.Thread(target=self._run)
        self._thread.daemon = True
        self._thread.start()

    def stop(self) -> None:
        if not self._running:
            return

        self._running = False

        if self._thread is not None:
            self._thread.join()
            self._thread = None
