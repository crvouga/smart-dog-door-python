from src.image_classifier.interface import ImageClassifier
from src.device_camera.interface import DeviceCamera
from src.device_door.interface import DeviceDoor
from dataclasses import dataclass


@dataclass
class Deps:
    image_classifier: ImageClassifier
    device_camera: DeviceCamera
    device_door: DeviceDoor
