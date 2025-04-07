import os
from dotenv import load_dotenv
from dataclasses import dataclass
from src.library.secret_string import SecretString
from typing import Any


@dataclass
class Env:
    wyze_key_id: SecretString
    wyze_api_key: SecretString
    wyze_email: SecretString
    wyze_password: SecretString


def load_env() -> Env:
    load_dotenv()

    wyze_key_id = SecretString(
        name="wyze_key_id", secret=_ensure_non_empty_string(os.getenv("WYZE_KEY_ID"))
    )

    wyze_api_key = SecretString(
        name="wyze_api_key", secret=_ensure_non_empty_string(os.getenv("WYZE_API_KEY"))
    )

    wyze_email = SecretString(
        name="wyze_email", secret=_ensure_non_empty_string(os.getenv("WYZE_EMAIL"))
    )

    wyze_password = SecretString(
        name="wyze_password",
        secret=_ensure_non_empty_string(os.getenv("WYZE_PASSWORD")),
    )

    env = Env(
        wyze_key_id=wyze_key_id,
        wyze_api_key=wyze_api_key,
        wyze_email=wyze_email,
        wyze_password=wyze_password,
    )

    return env


def _ensure_non_empty_string(name: Any) -> str:
    if isinstance(name, str) and name:
        return name
    else:
        raise ValueError(f"{name} is not a non-empty string")
