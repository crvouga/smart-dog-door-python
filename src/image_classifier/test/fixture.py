from src.assets import assets_dir
from src.image.image import Image

# from src.image_classifier.impl_pretrained import (
#     PretrainedImageClassifier,
#     PretrainedModelName,
# )
from src.image_classifier.impl_yolo import YoloImageClassifier, YoloModelSize
from src.image_classifier.interface import ImageClassifier


class Fixture:
    image_classifier: ImageClassifier

    def __init__(self) -> None:
        self.image_classifier = YoloImageClassifier(
            model_size=YoloModelSize.EXTRA_LARGE,
        )
        # self.image_classifier = PretrainedImageClassifier(
        #     model_name=PretrainedModelName.EFFICIENTNET_B3,
        # )


def assert_dog(image_asset: str) -> None:
    f = Fixture()

    image = Image.from_file(assets_dir(image_asset))

    results = f.image_classifier.classify(images=[image])

    assert len(results) > 0

    result = max(results, key=lambda x: x.weight)

    assert "dog" in result.label


def assert_not_dog(image_asset: str) -> None:
    f = Fixture()

    image = Image.from_file(assets_dir(image_asset))

    results = f.image_classifier.classify(images=[image])

    if len(results) == 0:
        return

    result = max(results, key=lambda x: x.weight)

    assert "dog" not in result.label


def assert_cat(image_asset: str) -> None:
    f = Fixture()

    image = Image.from_file(assets_dir(image_asset))

    results = f.image_classifier.classify(images=[image])

    assert len(results) > 0

    result = max(results, key=lambda x: x.weight)

    assert "cat" in result.label


def assert_not_cat(image_asset: str) -> None:
    f = Fixture()

    image = Image.from_file(assets_dir(image_asset))

    results = f.image_classifier.classify(images=[image])

    if len(results) == 0:
        return

    result = max(results, key=lambda x: x.weight)

    assert "cat" not in result.label


def assert_empty(image_asset: str) -> None:
    f = Fixture()

    image = Image.from_file(assets_dir(image_asset))

    results = f.image_classifier.classify(images=[image])

    assert len(results) == 0


def assert_not_empty(image_asset: str) -> None:
    f = Fixture()

    image = Image.from_file(assets_dir(image_asset))

    results = f.image_classifier.classify(images=[image])

    assert len(results) != 0
