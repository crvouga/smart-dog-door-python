from src.image.image import Image
from src.image_classifier.classification import Classification
from src.image_classifier.test.fixture import Fixture


def _assert_cat(results: list[Classification]) -> None:
    result = max(results, key=lambda x: x.weight)

    assert "cat" in result.label


def _assert_not_cat(results: list[Classification]) -> None:
    result = max(results, key=lambda x: x.weight)

    assert "cat" not in result.label


def test_cat_clear_front() -> None:
    f = Fixture()

    images = [Image.from_file("./images/cat_clear_front/1.jpeg")]

    results = f.image_classifier.classify(images=images)

    _assert_cat(results)


def test_cat_clear_front_2() -> None:
    f = Fixture()

    images = [Image.from_file("./images/cat_clear_front/2.jpeg")]

    results = f.image_classifier.classify(images=images)

    _assert_cat(results)


def test_cat_security_footage_1() -> None:
    f = Fixture()

    images = [Image.from_file("./images/cat_security_footage/1.jpeg")]

    results = f.image_classifier.classify(images=images)

    _assert_cat(results)


def test_cat_security_footage_2() -> None:
    f = Fixture()

    images = [Image.from_file("./images/cat_security_footage/2.jpeg")]

    results = f.image_classifier.classify(images=images)

    _assert_cat(results)


def test_not_cat_dog_clear_front() -> None:
    f = Fixture()

    images = [Image.from_file("./images/dog_clear_front/1.jpeg")]

    results = f.image_classifier.classify(images=images)

    _assert_not_cat(results)
