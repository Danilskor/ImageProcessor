from typing import override

import numpy as np

from src.base.base_processor import BaseProcessor, BaseProcessorConfig
from src.base import InvalidGammaValueError


class GammaConfig(BaseProcessorConfig):
    def __init__(self, gamma: float):
        if gamma <= 0:
            raise InvalidGammaValueError("Gamma value must be positive")
        self.gamma = gamma


class GammaTransformation(BaseProcessor):
    def __init__(self, gamma: int | float = 1):
        super().__init__()
        self._config = GammaConfig(gamma)

    @override
    def process(self, image: np.ndarray) -> np.ndarray:
        # Correct formula: normalise → apply power → scale back.
        # cv2.pow(uint8, gamma) computes pixel_value^gamma which overflows
        # for bright pixels (e.g. 200^2 = 40 000 >> 255) and corrupts the heap.
        gamma = self._config.gamma
        lut = (np.arange(256, dtype=np.float32) / 255.0) ** gamma
        lut = np.clip(lut * 255.0, 0, 255).astype(np.uint8)
        import cv2
        return cv2.LUT(image, lut)
