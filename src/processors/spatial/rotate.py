from typing import override

import cv2
import numpy as np

from src.base.base_processor import BaseProcessor, BaseProcessorConfig


class RotateConfig(BaseProcessorConfig):
    def __init__(self, angle: float = 0.0, scale: float = 1.0, expand: bool = False):
        self.angle = angle
        self.scale = scale
        self.expand = expand


class RotateTransformation(BaseProcessor):
    def __init__(self, angle: float = 0.0, scale: float = 1.0, expand: bool = False):
        super().__init__()
        self._config = RotateConfig(angle, scale, expand)

    @override
    def process(self, image: np.ndarray) -> np.ndarray:
        h, w = image.shape[:2]
        cx, cy = w / 2, h / 2
        matrix = cv2.getRotationMatrix2D((cx, cy), self._config.angle, self._config.scale)

        if self._config.expand:
            cos = abs(matrix[0, 0])
            sin = abs(matrix[0, 1])
            new_w = int(h * sin + w * cos)
            new_h = int(h * cos + w * sin)
            matrix[0, 2] += new_w / 2 - cx
            matrix[1, 2] += new_h / 2 - cy
            out_size = (new_w, new_h)
        else:
            out_size = (w, h)

        return cv2.warpAffine(image, matrix, out_size)
