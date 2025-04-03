from src.image_classifier.impl_fake import ImageClassifierFake


def main():
    image_classifier = ImageClassifierFake()

    image_classifier.classify([])

    print("Hello, World!")
