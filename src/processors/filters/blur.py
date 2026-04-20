from typing import override

import cv2
import numpy as np

from src.base.base_processor import BaseProcessor, BaseProcessorConfig
from src.base import InvalidKernelSizeError

BLUR_TYPES = ("gaussian", "median", "box")


class BlurConfig(BaseProcessorConfig):
    def __init__(self, kernel_size: int = 5, blur_type: str = "gaussian"):
        if kernel_size < 1 or kernel_size % 2 == 0:
            raise InvalidKernelSizeError("kernel_size must be a positive odd integer")
        if blur_type not in BLUR_TYPES:
            raise ValueError(f"blur_type must be one of {BLUR_TYPES}")
        self.kernel_size = kernel_size
        self.blur_type = blur_type


class BlurTransformation(BaseProcessor):
    def __init__(self, kernel_size: int = 5, blur_type: str = "gaussian"):
        super().__init__()
        self._config = BlurConfig(kernel_size, blur_type)

    @override
    def process(self, image: np.ndarray) -> np.ndarray:
        k = self._config.kernel_size
        match self._config.blur_type:
            case "gaussian":
                return cv2.GaussianBlur(image, (k, k), 0)
            case "median":
                return cv2.medianBlur(image, k)
            case "box":
                return cv2.blur(image, (k, k))
            case _:
                return image
