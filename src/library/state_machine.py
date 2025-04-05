from typing import Callable, Generic, TypeVar, Optional, List
import queue
import threading
from src.library.life_cycle import LifeCycle
import logging
from src.library.pub_sub import PubSub, Sub

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
    _models: PubSub[Model]
    _msgs: PubSub[Msg]
    _should_log: bool

    def __init__(
        self,
        init: Callable[[], tuple[Model, List[Effect]]],
        transition: Callable[[Model, Msg], tuple[Model, List[Effect]]],
        interpret_effect: Callable[[Effect, queue.Queue[Msg]], None],
        logger: logging.Logger,
        should_log: bool = False,
    ) -> None:
        self._init = init
        self._transition = transition
        self._interpret_effect = interpret_effect
        self._msg_queue = queue.Queue[Msg]()
        self._model = None
        self._models = PubSub[Model]()
        self._msgs = PubSub[Msg]()
        self._running = False
        self._thread = None
        self._logger = logger.getChild("state_machine")
        self._should_log = should_log

    def _interpret_effect_thread(self, effect: Effect) -> None:
        if self._should_log:
            self._logger.info("Effect: %s", effect)

        thread = threading.Thread(
            target=self._interpret_effect, args=(effect, self._msg_queue)
        )
        thread.start()
        thread.join()

    def models(self) -> Sub[Model]:
        return self._models

    def msgs(self) -> Sub[Msg]:
        return self._msgs

    def _handle_output(self, model: Model, effects: List[Effect]) -> None:
        self._models.pub(model)
        self._model = model
        for effect in effects:
            self._interpret_effect_thread(effect)

    def _run(self) -> None:
        model, effects = self._init()

        self._handle_output(model, effects)

        for effect in effects:
            self._interpret_effect_thread(effect)

        while self._running:
            try:
                msg = self._msg_queue.get(timeout=0.1)

                if msg is None:
                    self._running = False
                    break

                if self._model is None:
                    continue

                self._msgs.pub(msg)
                model, effects = self._transition(self._model, msg)

                if self._should_log:
                    self._logger.info(
                        f"Transition:\n\tmodel={self._model.__dict__}\n\tmsg={msg.__dict__}\n\tnew_model={model.__dict__}\n\teffects=[{', '.join(str(effect.__dict__) for effect in effects)}]"
                    )
                self._handle_output(model, effects)

            except queue.Empty:
                continue

    def start(self) -> None:
        self._logger.info("Starting")
        if self._thread is not None and self._thread.is_alive():
            self._logger.info("Already started")
            return

        self._running = True
        self._thread = threading.Thread(target=self._run)
        self._thread.daemon = True
        self._thread.start()

        self._logger.info("Started")

    def stop(self) -> None:
        self._logger.info("Stopping")
        if not self._running:
            self._logger.info("Already stopped")
            return

        self._running = False

        if self._thread is not None:
            self._thread.join()
            self._thread = None

        self._logger.info("Stopped")
