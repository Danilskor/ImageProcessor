from typing import override

import cv2
import numpy as np

from src.base.base_processor import BaseProcessor, BaseProcessorConfig

MORPH_OPS = ("erode", "dilate", "open", "close", "gradient", "tophat", "blackhat")
MORPH_SHAPES = ("rect", "ellipse", "cross")

_CV_OP = {
    "erode":    cv2.MORPH_ERODE,
    "dilate":   cv2.MORPH_DILATE,
    "open":     cv2.MORPH_OPEN,
    "close":    cv2.MORPH_CLOSE,
    "gradient": cv2.MORPH_GRADIENT,
    "tophat":   cv2.MORPH_TOPHAT,
    "blackhat": cv2.MORPH_BLACKHAT,
}

_CV_SHAPE = {
    "rect":    cv2.MORPH_RECT,
    "ellipse": cv2.MORPH_ELLIPSE,
    "cross":   cv2.MORPH_CROSS,
}


class MorphologyConfig(BaseProcessorConfig):
    def __init__(
        self,
        operation: str = "erode",
        kernel_size: int = 3,
        kernel_shape: str = "rect",
        iterations: int = 1,
    ):
        if operation not in MORPH_OPS:
            raise ValueError(f"operation must be one of {MORPH_OPS}")
        if kernel_size < 1:
            raise ValueError("kernel_size must be >= 1")
        if kernel_shape not in MORPH_SHAPES:
            raise ValueError(f"kernel_shape must be one of {MORPH_SHAPES}")
        if iterations < 1:
            raise ValueError("iterations must be >= 1")
        self.operation = operation
        self.kernel_size = kernel_size
        self.kernel_shape = kernel_shape
        self.iterations = iterations


class MorphologyTransformation(BaseProcessor):
    """Morphological operations: erosion, dilation, opening, closing,
    morphological gradient, top-hat, and black-hat.

    Works on any image (BGR, grayscale, or binary).
    """

    def __init__(
        self,
        operation: str = "erode",
        kernel_size: int = 3,
        kernel_shape: str = "rect",
        iterations: int = 1,
    ):
        super().__init__()
        self._config = MorphologyConfig(operation, kernel_size, kernel_shape, iterations)

    @override
    def process(self, image: np.ndarray) -> np.ndarray:
        cfg = self._config
        kernel = cv2.getStructuringElement(
            _CV_SHAPE[cfg.kernel_shape],
            (cfg.kernel_size, cfg.kernel_size),
        )
        return cv2.morphologyEx(
            image,
            _CV_OP[cfg.operation],
            kernel,
            iterations=cfg.iterations,
        )
