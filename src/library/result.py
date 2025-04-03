from dataclasses import dataclass
from typing import Generic, TypeVar, Literal, Union, Callable, Any

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


Result = Union[Ok[T], Err[E]]


def attempt(operation: Callable[[], T]) -> Result[T, Exception]:
    try:
        value = operation()
        return Ok(value=value)
    except Exception as e:
        return Err(error=e)
