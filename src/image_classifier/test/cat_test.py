from src.image.image import Image
from src.image_classifier.classification import Classification
from src.image_classifier.test.fixture import Fixture


def test_cat_clear_front() -> None:
    f = Fixture()

    images = [Image.from_file("./images/cat_clear_front.jpeg")]

    results = f.image_classifier.classify(images=images)

    result = max(results, key=lambda x: x.weight)

    assert "cat" in result.label


def test_cat_clear_front() -> None:
    f = Fixture()

    images = [Image.from_file("./images/cat_security_footage.jpeg")]

    results = f.image_classifier.classify(images=images)

    result = max(results, key=lambda x: x.weight)

    assert "cat" in result.label
