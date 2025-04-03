from src.image_classifier.interface import ImageClassifier
from src.image_classifier.impl_fake import ImageClassifierFake


class Fixture:
    image_classifier: ImageClassifier

    def __init__(self):
        self.image_classifier = ImageClassifierFake()
