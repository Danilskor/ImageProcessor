from typing import override

import numpy as np

from src.base.base_processor import BaseProcessor, BaseProcessorConfig


class ExposureConfig(BaseProcessorConfig):
    def __init__(self, ev_stops: float = 0.0):
        self.ev_stops = ev_stops


class ExposureTransformation(BaseProcessor):
    def __init__(self, ev_stops: float = 0.0):
        super().__init__()
        self._config = ExposureConfig(ev_stops)

    @override
    def process(self, image: np.ndarray) -> np.ndarray:
        factor = 2.0 ** self._config.ev_stops
        result = image.astype(np.float32) * factor
        return np.clip(result, 0, 255).astype(np.uint8)
