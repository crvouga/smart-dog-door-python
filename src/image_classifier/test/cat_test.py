from src.assets import assets_dir
from src.image.image import Image
from src.image_classifier.classification import Classification
from src.image_classifier.test.fixture import Fixture


def _test_cat(image_asset: str) -> None:
    f = Fixture()

    image = Image.from_file(assets_dir(image_asset))

    results = f.image_classifier.classify(images=[image])

    assert len(results) > 0

    result = max(results, key=lambda x: x.weight)

    assert "cat" in result.label


def _test_not_cat(image_asset: str) -> None:
    f = Fixture()

    image = Image.from_file(assets_dir(image_asset))

    results = f.image_classifier.classify(images=[image])

    if len(results) == 0:
        return

    result = max(results, key=lambda x: x.weight)

    assert "cat" not in result.label


def test_cat_clear_front() -> None:
    _test_cat("images/cat_clear_front/1.jpeg")


def test_cat_clear_front_2() -> None:
    _test_cat("images/cat_clear_front/2.jpeg")


def test_cat_security_footage_1() -> None:
    _test_cat("images/cat_security_footage/1.jpeg")


def test_cat_security_footage_2() -> None:
    _test_cat("images/cat_security_footage/2.jpeg")


def test_cat_security_footage_3() -> None:
    _test_cat("images/cat_security_footage/3.jpeg")


def test_not_cat_dog_clear_front() -> None:
    _test_not_cat("images/dog_clear_front/1.jpeg")


def test_not_cat_person_clear_front() -> None:
    _test_not_cat("images/person_clear_front/1.jpeg")
