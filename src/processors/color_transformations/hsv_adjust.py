from typing import override

import cv2
import numpy as np

from src.base.base_processor import BaseProcessor, BaseProcessorConfig


class HSVAdjustConfig(BaseProcessorConfig):
    def __init__(
        self,
        hue_shift: float = 0.0,
        saturation_scale: float = 1.0,
        value_scale: float = 1.0,
    ):
        self.hue_shift = hue_shift
        self.saturation_scale = saturation_scale
        self.value_scale = value_scale


class HSVAdjustTransformation(BaseProcessor):
    def __init__(
        self,
        hue_shift: float = 0.0,
        saturation_scale: float = 1.0,
        value_scale: float = 1.0,
    ):
        super().__init__()
        self._config = HSVAdjustConfig(hue_shift, saturation_scale, value_scale)

    @override
    def process(self, image: np.ndarray) -> np.ndarray:
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)

        hsv[..., 0] = (hsv[..., 0] + self._config.hue_shift) % 180
        hsv[..., 1] = np.clip(hsv[..., 1] * self._config.saturation_scale, 0, 255)
        hsv[..., 2] = np.clip(hsv[..., 2] * self._config.value_scale, 0, 255)

        return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
