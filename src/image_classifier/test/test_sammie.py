from src.image_classifier.test.fixture import assert_dog


def test_sammie_1() -> None:
    assert_dog("images/dog_sammie/1.jpeg")
