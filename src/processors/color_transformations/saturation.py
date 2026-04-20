from typing import override

import cv2
import numpy as np

from src.base.base_processor import BaseProcessor, BaseProcessorConfig


class SaturationConfig(BaseProcessorConfig):
    def __init__(self, scale: float = 1.0):
        if scale < 0:
            raise ValueError("scale must be non-negative")
        self.scale = scale


class SaturationTransformation(BaseProcessor):
    """Scale saturation channel only (HSV S), leaving hue and value unchanged."""

    def __init__(self, scale: float = 1.0):
        super().__init__()
        self._config = SaturationConfig(scale)

    @override
    def process(self, image: np.ndarray) -> np.ndarray:
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[..., 1] = np.clip(hsv[..., 1] * self._config.scale, 0, 255)
        return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
