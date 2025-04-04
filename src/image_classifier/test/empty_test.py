from src.assets import assets_dir
from src.image.image import Image
from src.image_classifier.classification import Classification
from src.image_classifier.test.fixture import Fixture


def _test_empty(image_asset: str) -> None:
    f = Fixture()

    image = Image.from_file(assets_dir(image_asset))

    results = f.image_classifier.classify(images=[image])

    assert len(results) == 0


def _test_not_empty(image_asset: str) -> None:
    f = Fixture()

    image = Image.from_file(assets_dir(image_asset))

    results = f.image_classifier.classify(images=[image])

    assert len(results) != 0


def test_empty_security_footage_1() -> None:
    _test_empty("images/empty_security_footage/1.jpeg")


def test_empty_security_footage_2() -> None:
    _test_empty("images/empty_security_footage/2.jpeg")


def test_empty_security_footage_3() -> None:
    _test_empty("images/empty_security_footage/3.jpeg")


def test_not_empty_cat_security_footage() -> None:
    _test_not_empty("images/cat_security_footage/1.jpeg")


def test_not_empty_dog_security_footage() -> None:
    _test_not_empty("images/dog_security_footage/1.jpeg")
