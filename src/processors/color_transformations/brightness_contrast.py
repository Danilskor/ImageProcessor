from typing import override

import cv2
import numpy as np

from src.base.base_processor import BaseProcessor, BaseProcessorConfig


class BrightnessContrastConfig(BaseProcessorConfig):
    def __init__(self, alpha: float = 1.0, beta: float = 0.0):
        if alpha <= 0:
            raise ValueError("alpha (contrast) must be positive")
        self.alpha = alpha
        self.beta = beta


class BrightnessContrastTransformation(BaseProcessor):
    def __init__(self, alpha: float = 1.0, beta: float = 0.0):
        super().__init__()
        self._config = BrightnessContrastConfig(alpha, beta)

    @override
    def process(self, image: np.ndarray) -> np.ndarray:
        return cv2.convertScaleAbs(image, alpha=self._config.alpha, beta=self._config.beta)
