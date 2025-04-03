from dataclasses import dataclass
from typing import Generic, TypeVar, Literal, Union

T = TypeVar("T")
E = TypeVar("E", bound=Exception)


@dataclass(frozen=True)
class Ok(Generic[T]):
    value: T
    type: Literal["ok"] = "ok"


@dataclass(frozen=True)
class Err(Generic[E]):
    error: E
    type: Literal["err"] = "err"


class Result(Generic[T, E]):
    @staticmethod
    def success(value: T) -> "Result[T, E]":
        return Result(Ok(value))

    @staticmethod
    def failure(error: E) -> "Result[T, E]":
        return Result(Err(error))

    def __init__(self, result: Union[Ok[T], Err[E]]):
        self._result = result

    def is_ok(self) -> bool:
        return isinstance(self._result, Ok)

    def is_err(self) -> bool:
        return isinstance(self._result, Err)

    def unwrap(self) -> T:
        if isinstance(self._result, Ok):
            return self._result.value
        raise self._result.error


def attempt(operation: callable) -> Result[T, E]:
    try:
        value = operation()
        return Ok(value=value)
    except Exception as e:
        return Err(error=e)
