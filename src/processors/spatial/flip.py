from typing import override

import cv2
import numpy as np

from src.base.base_processor import BaseProcessor, BaseProcessorConfig


class FlipConfig(BaseProcessorConfig):
    def __init__(self, flip_code: int = 1):
        # 0: vertical, 1: horizontal, -1: both
        if flip_code not in (-1, 0, 1):
            raise ValueError("flip_code must be -1, 0, or 1")
        self.flip_code = flip_code


class FlipTransformation(BaseProcessor):
    def __init__(self, flip_code: int = 1):
        super().__init__()
        self._config = FlipConfig(flip_code)

    @override
    def process(self, image: np.ndarray) -> np.ndarray:
        return cv2.flip(image, self._config.flip_code)
