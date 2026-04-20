from typing import override

import numpy as np

from src.base.base_processor import BaseProcessor, BaseProcessorConfig
from src.base import InvalidCropRegionError


class CropConfig(BaseProcessorConfig):
    def __init__(self, x: int, y: int, width: int, height: int):
        if width <= 0 or height <= 0:
            raise InvalidCropRegionError("Crop width and height must be positive")
        if x < 0 or y < 0:
            raise InvalidCropRegionError("Crop x and y must be non-negative")
        self.x = x
        self.y = y
        self.width = width
        self.height = height


class CropTransformation(BaseProcessor):
    def __init__(self, x: int = 0, y: int = 0, width: int = 100, height: int = 100):
        super().__init__()
        self._config = CropConfig(x, y, width, height)

    @override
    def process(self, image: np.ndarray) -> np.ndarray:
        h, w = image.shape[:2]
        x = min(self._config.x, w - 1)
        y = min(self._config.y, h - 1)
        # Clamp so we always return at least a 1×1 image
        x2 = min(x + self._config.width, w)
        y2 = min(y + self._config.height, h)
        # Return a contiguous copy — a slice shares the original row-stride,
        # which breaks any downstream code that assumes stride == w * channels.
        return np.ascontiguousarray(image[y:y2, x:x2])
