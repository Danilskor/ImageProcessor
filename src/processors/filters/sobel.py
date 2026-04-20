from typing import override

import cv2
import numpy as np

from src.base.base_processor import BaseProcessor, BaseProcessorConfig
from src.base import InvalidKernelSizeError

SOBEL_DIRECTIONS = ("x", "y", "magnitude")
VALID_KSIZES = (1, 3, 5, 7)


class SobelConfig(BaseProcessorConfig):
    def __init__(
        self,
        direction: str = "magnitude",
        ksize: int = 3,
        scale: float = 1.0,
        delta: float = 0.0,
    ):
        if direction not in SOBEL_DIRECTIONS:
            raise ValueError(f"direction must be one of {SOBEL_DIRECTIONS}")
        if ksize not in VALID_KSIZES:
            raise InvalidKernelSizeError(f"ksize must be one of {VALID_KSIZES}")
        self.direction = direction
        self.ksize = ksize
        self.scale = scale
        self.delta = delta


class SobelTransformation(BaseProcessor):
    """Sobel derivative filter.

    direction="x"         — horizontal edges (∂/∂x)
    direction="y"         — vertical edges   (∂/∂y)
    direction="magnitude" — √(Gx² + Gy²), normalised to uint8
    """

    def __init__(
        self,
        direction: str = "magnitude",
        ksize: int = 3,
        scale: float = 1.0,
        delta: float = 0.0,
    ):
        super().__init__()
        self._config = SobelConfig(direction, ksize, scale, delta)

    @override
    def process(self, image: np.ndarray) -> np.ndarray:
        cfg = self._config
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        kw = dict(ddepth=cv2.CV_64F, ksize=cfg.ksize, scale=cfg.scale, delta=cfg.delta)

        if cfg.direction == "x":
            result = cv2.Sobel(gray, dx=1, dy=0, **kw)
            result = cv2.convertScaleAbs(result)
        elif cfg.direction == "y":
            result = cv2.Sobel(gray, dx=0, dy=1, **kw)
            result = cv2.convertScaleAbs(result)
        else:  # magnitude
            gx = cv2.Sobel(gray, dx=1, dy=0, **kw)
            gy = cv2.Sobel(gray, dx=0, dy=1, **kw)
            magnitude = np.sqrt(gx ** 2 + gy ** 2)
            result = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

        return cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)
