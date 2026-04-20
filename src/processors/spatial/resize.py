from typing import override

import cv2
import numpy as np

from src.base.base_processor import BaseProcessor, BaseProcessorConfig


class ResizeConfig(BaseProcessorConfig):
    def __init__(
        self,
        width: int,
        height: int,
        interpolation: int = cv2.INTER_LINEAR,
    ):
        if width <= 0 or height <= 0:
            raise ValueError("width and height must be positive")
        self.width = width
        self.height = height
        self.interpolation = interpolation


class ResizeTransformation(BaseProcessor):
    def __init__(
        self,
        width: int = 640,
        height: int = 480,
        interpolation: int = cv2.INTER_LINEAR,
    ):
        super().__init__()
        self._config = ResizeConfig(width, height, interpolation)

    @override
    def process(self, image: np.ndarray) -> np.ndarray:
        return cv2.resize(
            image,
            (self._config.width, self._config.height),
            interpolation=self._config.interpolation,
        )
