from typing import Generic, TypeVar, Union

T = TypeVar("T")
E = TypeVar("E", bound=Exception)


class Result(Generic[T, E]):
    __slots__ = ("_value", "_error")

    def __init__(self, value: T = None, error: E = None):
        object.__setattr__(self, "_value", value)
        object.__setattr__(self, "_error", error)

    def is_ok(self) -> bool:
        return self._error is None

    def is_err(self) -> bool:
        return self._error is not None

    def unwrap(self) -> T:
        if self._error:
            raise self._error
        return self._value

    # Prevent mutation
    def __setattr__(self, key, value):
        raise AttributeError("Result objects are immutable")
