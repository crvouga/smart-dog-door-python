from src.image_classifier.test.fixture import assert_cat, assert_not_cat
import pytest


@pytest.mark.slow
def test_cat_clear_front() -> None:
    assert_cat("images/cat_clear_front/1.jpeg")


@pytest.mark.slow
def test_cat_clear_front_2() -> None:
    assert_cat("images/cat_clear_front/2.jpeg")


@pytest.mark.slow
def test_cat_security_footage_1() -> None:
    assert_cat("images/cat_security_footage/1.jpeg")


@pytest.mark.slow
def test_cat_security_footage_2() -> None:
    assert_cat("images/cat_security_footage/2.jpeg")


@pytest.mark.slow
def test_cat_security_footage_3() -> None:
    assert_cat("images/cat_security_footage/3.jpeg")


@pytest.mark.slow
def test_not_cat_dog_clear_front() -> None:
    assert_not_cat("images/dog_clear_front/1.jpeg")


@pytest.mark.slow
def test_not_cat_person_clear_front() -> None:
    assert_not_cat("images/person_clear_front/1.jpeg")
