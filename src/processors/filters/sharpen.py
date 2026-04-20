from typing import override

import cv2
import numpy as np

from src.base.base_processor import BaseProcessor, BaseProcessorConfig


class SharpenConfig(BaseProcessorConfig):
    def __init__(self, strength: float = 1.0):
        if strength < 0:
            raise ValueError("strength must be non-negative")
        self.strength = strength


class SharpenTransformation(BaseProcessor):
    def __init__(self, strength: float = 1.0):
        super().__init__()
        self._config = SharpenConfig(strength)

    @override
    def process(self, image: np.ndarray) -> np.ndarray:
        blurred = cv2.GaussianBlur(image, (0, 0), sigmaX=3)
        return cv2.addWeighted(
            image, 1.0 + self._config.strength, blurred, -self._config.strength, 0
        )
