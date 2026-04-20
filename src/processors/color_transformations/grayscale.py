from typing import override

import cv2
import numpy as np

from src.base.base_processor import BaseProcessor, BaseProcessorConfig


class GrayscaleConfig(BaseProcessorConfig):
    def __init__(self):
        pass


class GrayscaleTransformation(BaseProcessor):
    """Convert image to grayscale. Outputs 3-channel BGR (all channels equal)
    so downstream pipeline steps continue to work."""

    def __init__(self):
        super().__init__()
        self._config = GrayscaleConfig()

    @override
    def process(self, image: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
