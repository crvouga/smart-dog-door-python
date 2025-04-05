import numpy as np
from PIL import Image as PILImage
import io
import base64
from typing import Optional, Union
import os


class Image:
    _array: np.ndarray
    _path: Optional[str]
    _pil_image: Optional[PILImage.Image]
    _bytes: Optional[bytes]

    def __init__(
        self,
        data: Optional[Union[np.ndarray, PILImage.Image, bytes]] = None,
        path: Optional[str] = None,
    ) -> None:
        """Initialize with numpy array, PIL image, path, or bytes"""
        self._path = None
        if path is not None:
            self._path = path
            self._load_from_path(path)
        elif data is not None:
            self._load_from_data(data)
        else:
            self._array = np.zeros((1, 1, 3), dtype=np.uint8)

    @classmethod
    def from_np_array(cls, data: np.ndarray) -> "Image":
        image = cls()
        image._array = data
        return image

    @classmethod
    def from_file(cls, path: str) -> "Image":
        image = cls()
        image._path = path
        image._load_from_path(path)
        return image

    def _load_from_path(self, path: str) -> None:
        """Load image from file path"""
        pil_image = PILImage.open(path)
        self._array = np.array(pil_image)

    def _load_from_data(self, data: Union[np.ndarray, PILImage.Image, bytes]) -> None:
        """Load from numpy array, PIL image, or bytes"""
        if isinstance(data, np.ndarray):
            self._array = data
        elif isinstance(data, PILImage.Image):
            self._array = np.array(data)
        elif isinstance(data, bytes):
            buffer = io.BytesIO(data)
            pil_image = PILImage.open(buffer)
            self._array = np.array(pil_image)
        else:
            raise TypeError(f"Unsupported data type: {type(data)}")

    @property
    def np_array(self) -> np.ndarray:
        """Get numpy array representation"""
        return self._array

    @property
    def pil_image(self) -> PILImage.Image:
        """Get PIL image representation"""
        return PILImage.fromarray(self._array)

    def to_bytes(self, format: str = "JPEG") -> bytes:
        """Convert to bytes with specified format"""
        buffer = io.BytesIO()
        self.pil_image.save(buffer, format=format)
        return buffer.getvalue()

    def to_base64(self, format: str = "JPEG") -> str:
        """Convert to base64 string"""
        return base64.b64encode(self.to_bytes(format)).decode("utf-8")

    @property
    def width(self) -> int:
        return self._array.shape[1]

    @property
    def height(self) -> int:
        return self._array.shape[0]

    @property
    def channels(self) -> int:
        return self._array.shape[2] if len(self._array.shape) > 2 else 1

    @property
    def filename(self) -> Optional[str]:
        """Get the filename if the image was loaded from a file"""
        if self._path is not None:
            return os.path.basename(self._path)
        return None
