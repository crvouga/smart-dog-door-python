import os
from dotenv import load_dotenv
from dataclasses import dataclass
from src.library.secret_string import SecretString


@dataclass
class Env:
    wyze_key_id: SecretString
    wyze_api_key: SecretString


def load_env() -> Env:
    load_dotenv()

    wyze_key_id_env_var = os.getenv("WYZE_KEY_ID")

    if wyze_key_id_env_var is None:
        raise ValueError("WYZE_KEY_ID is not set")

    wyze_key_id = SecretString(name="wyze_key_id", secret=wyze_key_id_env_var)

    wyze_api_key_env_var = os.getenv("WYZE_API_KEY")

    if wyze_api_key_env_var is None:
        raise ValueError("WYZE_API_KEY is not set")

    wyze_api_key = SecretString(name="wyze_api_key", secret=wyze_api_key_env_var)

    env = Env(
        wyze_key_id=wyze_key_id,
        wyze_api_key=wyze_api_key,
    )

    return env
