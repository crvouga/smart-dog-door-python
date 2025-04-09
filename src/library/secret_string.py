from typing import Any


class SecretString:
    _name: str
    _secret: str

    def __init__(self, name: str, secret: str) -> None:
        self._name = name
        self._secret = secret

    def __str__(self) -> str:
        return f"SecretString({self._name})"

    def __repr__(self) -> str:
        return f"SecretString({self._name})"

    def dangerously_read_secret(self) -> str:
        return self._secret
