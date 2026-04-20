from typing import override

import cv2
import numpy as np

from src.base.base_processor import BaseProcessor, BaseProcessorConfig

SKELETON_METHODS = ("zhang_suen", "guo_hall", "morphological")


class SkeletonConfig(BaseProcessorConfig):
    def __init__(self, method: str = "zhang_suen"):
        if method not in SKELETON_METHODS:
            raise ValueError(f"method must be one of {SKELETON_METHODS}")
        self.method = method


class SkeletonTransformation(BaseProcessor):
    """Skeletonize / thin a binary image.

    Expects a binary or grayscale image (any non-zero pixel treated as
    foreground).  Output is a BGR image where the skeleton is white on black.

    Methods:
      zhang_suen   — Zhang-Suen thinning  (cv2.ximgproc)
      guo_hall     — Guo-Hall thinning    (cv2.ximgproc)
      morphological — iterative erosion-based morphological skeleton
    """

    def __init__(self, method: str = "zhang_suen"):
        super().__init__()
        self._config = SkeletonConfig(method)

    @override
    def process(self, image: np.ndarray) -> np.ndarray:
        cfg = self._config

        # Convert to single-channel binary
        if image.ndim == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()

        # Binarise: any non-zero → 255
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY)

        method = cfg.method
        if method in ("zhang_suen", "guo_hall"):
            thinning_type = (
                cv2.ximgproc.THINNING_ZHANGSUEN
                if method == "zhang_suen"
                else cv2.ximgproc.THINNING_GUOHALL
            )
            skeleton = cv2.ximgproc.thinning(binary, thinningType=thinning_type)
        else:  # morphological
            skeleton = _morphological_skeleton(binary)

        return cv2.cvtColor(skeleton, cv2.COLOR_GRAY2BGR)


def _morphological_skeleton(binary: np.ndarray) -> np.ndarray:
    """Morphological skeleton via iterative erosion + opening."""
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    img = binary.copy()
    skeleton = np.zeros_like(img)

    while True:
        eroded = cv2.erode(img, kernel)
        opened = cv2.dilate(eroded, kernel)
        temp = cv2.subtract(img, opened)
        skeleton = cv2.bitwise_or(skeleton, temp)
        img = eroded
        if cv2.countNonZero(img) == 0:
            break

    return skeleton
