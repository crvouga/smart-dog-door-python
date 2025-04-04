from abc import ABC, abstractmethod
from typing import TypeVar, Callable, Generic, List
import queue

T = TypeVar("T")
U = TypeVar("U")


class Pub(ABC, Generic[T]):
    @abstractmethod
    def pub(self, value: T) -> None:
        pass


class Sub(ABC, Generic[T]):
    @abstractmethod
    def sub(self, observer: Callable[[T], None]) -> Callable[[], None]:
        pass

    @abstractmethod
    def enqueue(self, q: queue.Queue[T]) -> Callable[[], None]:
        """Subscribe to Sub and enqueue messages onto the given queue forever."""
        pass

    @abstractmethod
    def map(self, mapper: Callable[[T], U]) -> "Sub[U]":
        """Map messages from one type to another."""
        pass


class PubSub(Sub[T], Pub[T]):
    def __init__(self) -> None:
        self._subs: list[Callable[[T], None]] = []
        self._pending_messages: List[T] = []

    def sub(self, observer: Callable[[T], None]) -> Callable[[], None]:
        if observer not in self._subs:
            self._subs.append(observer)

            for message in self._pending_messages:
                observer(message)

            if self._pending_messages and self._subs:
                self._pending_messages = []

        def unsub() -> None:
            if observer in self._subs:
                self._subs.remove(observer)

        return unsub

    def pub(self, value: T) -> None:
        if not self._subs:
            self._pending_messages.append(value)
        else:
            for observer in self._subs:
                observer(value)

    def enqueue(self, q: queue.Queue[T]) -> Callable[[], None]:
        """Subscribe to PubSub and enqueue messages onto the given queue forever."""

        def enqueue_message(value: T) -> None:
            q.put(value)

        return self.sub(enqueue_message)

    def map(self, mapper: Callable[[T], U]) -> "PubSub[U]":
        new_pub_sub = PubSub[U]()

        def new_observer(value: T) -> None:
            new_value = mapper(value)
            new_pub_sub.pub(new_value)

        self.sub(new_observer)
        return new_pub_sub
