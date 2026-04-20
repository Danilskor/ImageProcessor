from typing import override

import cv2
import numpy as np

from src.base.base_processor import BaseProcessor, BaseProcessorConfig

SIMPLE_TYPES: dict[str, int] = {
    "Binary":        cv2.THRESH_BINARY,
    "Binary Inv":    cv2.THRESH_BINARY_INV,
    "Truncate":      cv2.THRESH_TRUNC,
    "To Zero":       cv2.THRESH_TOZERO,
    "To Zero Inv":   cv2.THRESH_TOZERO_INV,
}

ADAPTIVE_METHODS: dict[str, int] = {
    "Gaussian": cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    "Mean":     cv2.ADAPTIVE_THRESH_MEAN_C,
}

MODES = ("simple", "otsu", "adaptive")


class ThresholdConfig(BaseProcessorConfig):
    def __init__(
        self,
        mode: str = "simple",
        threshold: float = 127.0,
        max_val: float = 255.0,
        thresh_type: str = "Binary",
        adaptive_method: str = "Gaussian",
        block_size: int = 11,
        C: float = 2.0,
    ):
        if mode not in MODES:
            raise ValueError(f"mode must be one of {MODES}")
        if thresh_type not in SIMPLE_TYPES:
            raise ValueError(f"thresh_type must be one of {list(SIMPLE_TYPES)}")
        if adaptive_method not in ADAPTIVE_METHODS:
            raise ValueError(f"adaptive_method must be one of {list(ADAPTIVE_METHODS)}")
        if block_size < 3 or block_size % 2 == 0:
            raise ValueError("block_size must be an odd integer >= 3")
        self.mode = mode
        self.threshold = threshold
        self.max_val = max_val
        self.thresh_type = thresh_type
        self.adaptive_method = adaptive_method
        self.block_size = block_size
        self.C = C


class ThresholdTransformation(BaseProcessor):
    def __init__(
        self,
        mode: str = "simple",
        threshold: float = 127.0,
        max_val: float = 255.0,
        thresh_type: str = "Binary",
        adaptive_method: str = "Gaussian",
        block_size: int = 11,
        C: float = 2.0,
    ):
        super().__init__()
        self._config = ThresholdConfig(
            mode, threshold, max_val, thresh_type, adaptive_method, block_size, C
        )

    @override
    def process(self, image: np.ndarray) -> np.ndarray:
        cfg = self._config
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        if cfg.mode == "adaptive":
            result = cv2.adaptiveThreshold(
                gray,
                cfg.max_val,
                ADAPTIVE_METHODS[cfg.adaptive_method],
                SIMPLE_TYPES[cfg.thresh_type],
                cfg.block_size,
                cfg.C,
            )
        elif cfg.mode == "otsu":
            flags = SIMPLE_TYPES[cfg.thresh_type] | cv2.THRESH_OTSU
            _, result = cv2.threshold(gray, 0, cfg.max_val, flags)
        else:  # simple
            _, result = cv2.threshold(
                gray, cfg.threshold, cfg.max_val, SIMPLE_TYPES[cfg.thresh_type]
            )

        return cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)
