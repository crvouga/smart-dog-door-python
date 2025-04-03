from src.image_classifier.impl_fake import ImageClassifierFake


class Fixture:
    image_classifier: ImageClassifierFake

    def __init__(self):
        self.image_classifier = ImageClassifierFake()
