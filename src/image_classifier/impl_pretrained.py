import timm  # type: ignore
import torch  # type: ignore
from PIL import Image as PILImage
import torchvision.transforms as T  # type: ignore
from typing import List, Iterator, Dict, Tuple
import logging

from src.image.image import Image
from src.image_classifier.bounding_box import (
    BoundingBox,
)  # Keep for interface compatibility
from .interface import ImageClassifier, Classification

# --- Configuration ---

# Choose a powerful model from timm (see timm docs for options)
# Examples: 'vit_large_patch16_224.augreg_in21k_ft_in1k', 'swin_large_patch4_window7_224.ms_in22k_ft_in1k', 'convnext_large.fb_in22k_ft_in1k'
DEFAULT_MODEL_NAME = "vit_large_patch16_224.augreg_in21k_ft_in1k"

# Define ImageNet indices roughly corresponding to cats and dogs
# These can vary slightly. For precise mapping, consult the specific model's documentation or class map.
# Common ranges: Cat ~281-285, Dog ~151-275
CAT_INDICES = list(range(281, 286))
DOG_INDICES = list(range(151, 276))

# --- Implementation ---


class PretrainedClassifier(ImageClassifier):
    def __init__(
        self,
        model_name: str = DEFAULT_MODEL_NAME,
        device: str = "cuda" if torch.cuda.is_available() else "cpu",
        logger: logging.Logger = logging.getLogger(__name__),
    ) -> None:
        self._device = device
        self._model_name = model_name
        self._cat_indices = CAT_INDICES
        self._dog_indices = DOG_INDICES
        self._logger = logger

        self._logger.info(f"Using device: {self._device}")
        self._logger.info(f"Loading pre-trained model: {model_name}")

        try:
            self._model = timm.create_model(model_name, pretrained=True)
            self._model = self._model.to(self._device)
            self._model.eval()  # Set model to evaluation mode

            # Get model-specific preprocessing steps
            data_config = timm.data.resolve_model_data_config(self._model)
            self._transforms = timm.data.create_transform(
                **data_config, is_training=False
            )
            self._logger.info(f"Model {model_name} loaded successfully.")
            self._logger.info(f"Input size: {data_config.get('input_size')}")
            self._logger.info(f"Interpolation: {data_config.get('interpolation')}")
            self._logger.info(f"Mean: {data_config.get('mean')}")
            self._logger.info(f"Std: {data_config.get('std')}")

        except Exception as e:
            self._logger.error(
                f"Failed to load model '{model_name}': {e}", exc_info=True
            )
            raise

    def classify(self, images: list[Image]) -> list[Classification]:
        classifications: List[Classification] = []
        if not images:
            return classifications

        self._logger.info(f"Classifying {len(images)} image(s)...")
        with torch.no_grad():  # Disable gradient calculations for inference
            for i, image in enumerate(images):
                try:
                    pil_image = image.pil_image
                    if pil_image is None:
                        self._logger.warning(
                            f"Skipping image {i} as PIL image is None."
                        )
                        continue

                    # Apply preprocessing
                    input_tensor = self._transforms(pil_image).unsqueeze(
                        0
                    )  # Add batch dimension
                    input_tensor = input_tensor.to(self._device)

                    # Run inference
                    output = self._model(input_tensor)
                    # Apply Softmax to get probabilities
                    probabilities = torch.nn.functional.softmax(output[0], dim=0)

                    # Check probabilities for cat/dog classes
                    prob_cat = torch.sum(probabilities[self._cat_indices]).item()
                    prob_dog = torch.sum(probabilities[self._dog_indices]).item()

                    label = "unknown"
                    confidence = 0.0

                    if prob_cat > prob_dog:
                        label = "cat"
                        confidence = prob_cat
                    elif prob_dog > prob_cat:
                        label = "dog"
                        confidence = prob_dog
                    # Else: remains unknown with 0 confidence

                    self._logger.debug(
                        f"Image {i}: Cat Prob={prob_cat:.4f}, Dog Prob={prob_dog:.4f} -> Label='{label}', Conf={confidence:.4f}"
                    )

                    # Create placeholder bounding box covering the whole image (0.0 to 1.0)
                    # as this classifier doesn't provide localization.
                    placeholder_bbox = BoundingBox(
                        x_min=0.0, y_min=0.0, x_max=1.0, y_max=1.0
                    )

                    # Only add classification if label is known
                    if label != "unknown":
                        classifications.append(
                            Classification(
                                label=label,
                                weight=confidence,
                                bounding_box=placeholder_bbox,
                            )
                        )

                except Exception as e:
                    self._logger.error(
                        f"Error processing image {i}: {e}", exc_info=True
                    )

        self._logger.info(
            f"Classification complete. Found {len(classifications)} cats/dogs."
        )
        return classifications
