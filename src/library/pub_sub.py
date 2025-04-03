from abc import ABC, abstractmethod
from typing import TypeVar, Callable, Generic

T = TypeVar("T")


class Pub(ABC, Generic[T]):
    @abstractmethod
    def pub(self, value: T):
        pass


class Sub(ABC, Generic[T]):
    @abstractmethod
    def sub(self, observer: Callable[[T], None]) -> Callable[[], None]:
        pass


class PubSub(Sub[T], Pub[T]):
    def __init__(self):
        self._subs: list[Callable[[T], None]] = []

    def sub(self, observer: Callable[[T], None]) -> Callable[[], None]:
        if observer not in self._subs:
            self._subs.append(observer)

        def unsub():
            if observer in self._subs:
                self._subs.remove(observer)

        return unsub

    def pub(self, value: T):
        for observer in self._subs:
            observer(value)
