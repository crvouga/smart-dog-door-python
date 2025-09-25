from src.image_classifier.test.fixture import assert_empty, assert_not_empty
import pytest


@pytest.mark.slow
def test_empty_security_footage_1() -> None:
    assert_empty("images/empty_security_footage/1.jpeg")


@pytest.mark.slow
def test_empty_security_footage_2() -> None:
    assert_empty("images/empty_security_footage/2.jpeg")


@pytest.mark.slow
def test_empty_security_footage_3() -> None:
    assert_empty("images/empty_security_footage/3.jpeg")


@pytest.mark.slow
def test_not_empty_cat_security_footage() -> None:
    assert_not_empty("images/cat_security_footage/1.jpeg")


@pytest.mark.slow
def test_not_empty_dog_security_footage() -> None:
    assert_not_empty("images/dog_security_footage/1.jpeg")
