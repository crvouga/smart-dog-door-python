from dataclasses import dataclass
from src.library.secret_string import SecretString


@dataclass
class WyzeClientConfig:
    email: str
    password: SecretString
    key_id: str
    api_key: SecretString
