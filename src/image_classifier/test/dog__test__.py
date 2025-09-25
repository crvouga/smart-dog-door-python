from src.image_classifier.test.fixture import assert_dog, assert_not_dog
import pytest


@pytest.mark.slow
def test_dog_clear_front() -> None:
    assert_dog("images/dog_clear_front/1.jpeg")


@pytest.mark.slow
def test_dog_clear_front_2() -> None:
    assert_dog("images/dog_clear_front/2.jpeg")


@pytest.mark.slow
def test_dog_security_footage_1() -> None:
    assert_dog("images/dog_security_footage/1.jpeg")


@pytest.mark.slow
def test_dog_security_footage_2() -> None:
    assert_dog("images/dog_security_footage/2.jpeg")


@pytest.mark.slow
def test_dog_security_footage_3() -> None:
    assert_dog("images/dog_security_footage/3.jpeg")


@pytest.mark.slow
def test_not_dog_dog_clear_front() -> None:
    assert_not_dog("images/cat_clear_front/1.jpeg")


@pytest.mark.slow
def test_not_dog_person_clear_front() -> None:
    assert_not_dog("images/person_clear_front/1.jpeg")
