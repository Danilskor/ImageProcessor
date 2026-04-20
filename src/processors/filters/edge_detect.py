from typing import override

import cv2
import numpy as np

from src.base.base_processor import BaseProcessor, BaseProcessorConfig

EDGE_METHODS = ("canny", "sobel", "laplacian")


class EdgeDetectConfig(BaseProcessorConfig):
    def __init__(
        self,
        method: str = "canny",
        threshold1: float = 100.0,
        threshold2: float = 200.0,
    ):
        if method not in EDGE_METHODS:
            raise ValueError(f"method must be one of {EDGE_METHODS}")
        self.method = method
        self.threshold1 = threshold1
        self.threshold2 = threshold2


class EdgeDetectTransformation(BaseProcessor):
    def __init__(
        self,
        method: str = "canny",
        threshold1: float = 100.0,
        threshold2: float = 200.0,
    ):
        super().__init__()
        self._config = EdgeDetectConfig(method, threshold1, threshold2)

    @override
    def process(self, image: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        match self._config.method:
            case "canny":
                edges = cv2.Canny(gray, self._config.threshold1, self._config.threshold2)
            case "sobel":
                sx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
                sy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
                edges = np.clip(np.sqrt(sx**2 + sy**2), 0, 255).astype(np.uint8)
            case "laplacian":
                edges = cv2.convertScaleAbs(cv2.Laplacian(gray, cv2.CV_64F))
            case _:
                return image
        return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
