from src.image.image import Image
from src.image_classifier.impl_fake import ImageClassifierFake
from src.image_classifier.classification import Classification
from src.image_classifier.test.images.fixture import Fixture


def test_classify_returns_fake_classification():
    f = Fixture()
    classifier = f.image_classifier
    images = [Image()]

    result = classifier.classify(images)

    assert len(result) == 1
    assert isinstance(result[0], Classification)
    assert result[0].label == "fake"
    assert result[0].weight == 0.5
