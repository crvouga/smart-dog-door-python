from typing import Any, Callable


def recursive_map(obj: Any, mapper: Callable[[Any], Any]) -> Any:
    if isinstance(obj, dict):
        return {k: recursive_map(v, mapper) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [recursive_map(v, mapper) for v in obj]
    else:
        return mapper(obj)
