from src.library.secret_string import SecretString


def test_secret_string_init() -> None:
    """Test that SecretString initializes with name and secret."""
    secret = SecretString("test_secret", "my_secret_value")
    assert secret._name == "test_secret"
    assert secret._secret == "my_secret_value"


def test_secret_string_str() -> None:
    """Test that SecretString string representation shows name but not secret."""
    secret = SecretString("test_secret", "my_secret_value")
    assert str(secret) == "SecretString(test_secret)"


def test_secret_string_repr() -> None:
    """Test that SecretString representation shows name but not secret."""
    secret = SecretString("test_secret", "my_secret_value")
    assert repr(secret) == "SecretString(test_secret)"


def test_secret_string_dangerously_read_secret() -> None:
    """Test that dangerously_read_secret returns the actual secret value."""
    secret = SecretString("test_secret", "my_secret_value")
    assert secret.dangerously_read_secret() == "my_secret_value"
