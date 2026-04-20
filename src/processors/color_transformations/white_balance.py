from typing import override

import numpy as np

from src.base.base_processor import BaseProcessor, BaseProcessorConfig


class WhiteBalanceConfig(BaseProcessorConfig):
    def __init__(self, r_gain: float = 1.0, g_gain: float = 1.0, b_gain: float = 1.0):
        if any(g < 0 for g in (r_gain, g_gain, b_gain)):
            raise ValueError("Channel gains must be non-negative")
        self.r_gain = r_gain
        self.g_gain = g_gain
        self.b_gain = b_gain


class WhiteBalanceTransformation(BaseProcessor):
    def __init__(self, r_gain: float = 1.0, g_gain: float = 1.0, b_gain: float = 1.0):
        super().__init__()
        self._config = WhiteBalanceConfig(r_gain, g_gain, b_gain)

    @override
    def process(self, image: np.ndarray) -> np.ndarray:
        result = image.astype(np.float32)
        # OpenCV uses BGR channel order
        result[..., 0] *= self._config.b_gain
        result[..., 1] *= self._config.g_gain
        result[..., 2] *= self._config.r_gain
        return np.clip(result, 0, 255).astype(np.uint8)
